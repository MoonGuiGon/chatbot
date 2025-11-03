/**
 * Type definitions
 */

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  metadata?: MessageMetadata
  created_at: string
}

export interface MessageMetadata {
  sources?: Source[]
  query_intent?: string
  material_data?: MaterialData[]
  documents?: DocumentReference[]
}

export interface Source {
  type: 'mongodb' | 'document'
  material_id?: string
  source?: string
  data?: any
  metadata?: any
}

export interface MaterialData {
  materialId: string
  name: string
  category: string
  specifications?: Record<string, any>
  supplier?: string
  inventory?: InventoryInfo
  purchase_history?: PurchaseRecord[]
  usage_history?: UsageRecord[]
  installation_history?: InstallationRecord[]
}

export interface InventoryInfo {
  current_stock: number
  minimum_stock: number
  location: string
}

export interface PurchaseRecord {
  date: string
  quantity: number
  price: number
}

export interface UsageRecord {
  date: string
  equipment: string
  quantity: number
}

export interface InstallationRecord {
  date: string
  equipment: string
  location: string
}

export interface DocumentReference {
  source: string
}

export interface Conversation {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
  is_archived?: boolean
  messages?: Message[]
}

export interface ProgressStep {
  step: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  message: string
}

export interface UserSettings {
  user_id: number
  custom_prompts: string[]
  preferences: Record<string, any>
}

export interface Feedback {
  id?: number
  message_id?: number
  rating?: number
  comment?: string
  improved_response?: string
}

export interface StreamEvent {
  type: 'progress' | 'response' | 'error'
  step?: string
  status?: string
  message?: string
  response?: string
  sources?: Source[]
  material_data?: MaterialData[]
  documents?: any[]
  query_intent?: string
}
