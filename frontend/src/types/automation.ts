export interface ActionResult {
  success: boolean;
  message: string;
  data?: any;
  confirmation_required?: boolean;
  action_description?: string;
}
