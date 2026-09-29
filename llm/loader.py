"""
Local LLM loader for Ines.
Loads open-weight models (Mistral 7B / Gemma 2B) with optional
4-bit or 8-bit quantization using bitsandbytes.
"""

from typing import Optional, Any
import torch

from core import config, logger
from core.constants import MODEL_MISTRAL_7B, MODEL_GEMMA_2B
from llm.tokenizer_wrapper import TokenizerWrapper


class ModelLoader:
    """
    Loads and manages a local HuggingFace language model.
    Supports 4-bit quantization for consumer GPU hardware,
    and falls back to CPU if no CUDA GPU is available.
    """

    def __init__(self):
        self.model: Optional[Any] = None
        self.tokenizer_wrapper: Optional[TokenizerWrapper] = None
        self.model_name: str = config.model_name
        self.device: str = self._resolve_device()
        self._is_loaded: bool = False

    def _resolve_device(self) -> str:
        """Auto-detect available device, respecting config override."""
        preferred = config.device
        if preferred == "cuda" and not torch.cuda.is_available():
            logger.warning(
                "CUDA not available on this machine. Falling back to CPU. "
                "Inference will be slower. Consider using Gemma-2-2B for faster CPU speeds."
            )
            return "cpu"
        return preferred

    def load(self, model_name: Optional[str] = None, force_reload: bool = False) -> None:
        """
        Load the model and tokenizer into memory.

        Args:
            model_name: Override the model name from config.
            force_reload: If True, reload even if already loaded.
        """
        if self._is_loaded and not force_reload:
            logger.info(f"Model already loaded: {self.model_name}")
            return

        target_model = model_name or self.model_name
        logger.info(f"Loading model: {target_model} | Device: {self.device} | Quantization: {config.quantization}")

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                target_model,
                token=config.hf_token,
                trust_remote_code=True,
            )
            self.tokenizer_wrapper = TokenizerWrapper(tokenizer, target_model)

            # Quantization config
            model_kwargs: dict = {
                "token": config.hf_token,
                "trust_remote_code": True,
            }

            # Check if accelerate is available
            try:
                import accelerate
                has_accelerate = True
            except ImportError:
                has_accelerate = False

            quant = config.quantization
            if self.device != "cpu" and quant in ("4bit", "8bit"):
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=(quant == "4bit"),
                    load_in_8bit=(quant == "8bit"),
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                model_kwargs["quantization_config"] = bnb_config
                if has_accelerate:
                    model_kwargs["device_map"] = "auto"
            elif self.device == "cpu":
                # On CPU, standard PyTorch loads directly to RAM without device_map
                model_kwargs["torch_dtype"] = torch.float32
            else:
                model_kwargs["torch_dtype"] = torch.float16
                if has_accelerate:
                    model_kwargs["device_map"] = "auto"

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(target_model, **model_kwargs)
            self.model.eval()
            self.model_name = target_model
            self._is_loaded = True

            gpu_mem = ""
            if self.device != "cpu" and torch.cuda.is_available():
                vram_gb = torch.cuda.memory_allocated() / 1e9
                gpu_mem = f" | VRAM used: {vram_gb:.2f} GB"

            logger.info(f"Model loaded successfully: {target_model}{gpu_mem}")

        except ImportError as e:
            logger.error(
                f"Missing dependencies: {e}. "
                "Run: pip install transformers accelerate bitsandbytes"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load model '{target_model}': {e}")
            raise

    def switch_to_alternate(self) -> None:
        """
        Switch from the primary to the alternate (smaller) model.
        Useful for low-VRAM scenarios or quick testing.
        """
        alt = config.alternate_model_name
        logger.info(f"Switching to alternate model: {alt}")
        self.unload()
        self.load(model_name=alt)

    def unload(self) -> None:
        """Release model from GPU/CPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer_wrapper is not None:
            self.tokenizer_wrapper = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self._is_loaded = False
        logger.info("Model unloaded and memory cleared.")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def __repr__(self) -> str:
        status = "loaded" if self._is_loaded else "not loaded"
        return f"<ModelLoader model='{self.model_name}' device='{self.device}' status='{status}'>"
