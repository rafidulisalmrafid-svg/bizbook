export type Role = 'OWNER' | 'ADMIN' | 'MANAGER' | 'MEMBER' | 'VIEWER' | 'TENDER_MANAGER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  company_id: string;
  role: Role;
  full_name: string;
  email: string;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  is_active: boolean;
  created_at: string;
  profile?: CompanyProfile;
  brand?: CompanyBrand;
}

export interface CompanyProfile {
  id: string;
  company_id: string;
  registration_number?: string;
  tax_id?: string;
  established_year?: number;
  legal_structure?: string;
  primary_industry?: string;
  overview?: string;
  mission?: string;
  vision?: string;
  website?: string;
  address?: string;
  annual_turnover?: string;
}

export interface CompanyBrand {
  id: string;
  company_id: string;
  primary_color: string;
  secondary_color: string;
  font_family: string;
  logo_url?: string;
  dark_logo_url?: string;
  icon_url?: string;
}

export interface CompanyContact {
  id: string;
  company_id: string;
  contact_type: string;
  label: string;
  value: string;
  is_primary: boolean;
}

export interface CompanySignature {
  id: string;
  company_id: string;
  name: string;
  designation: string;
  signature_image_url: string;
  is_active: boolean;
}

export interface CompanySeal {
  id: string;
  company_id: string;
  name: string;
  seal_image_url: string;
  is_active: boolean;
}

export interface TeamMember {
  id: string;
  company_id: string;
  full_name: string;
  email?: string;
  phone?: string;
  designation: string;
  department?: string;
  bio?: string;
  skills: string[];
  is_active: boolean;
  is_archived: boolean;
  created_at: string;
  experiences: TeamExperience[];
  certifications: TeamCertification[];
}

export interface TeamExperience {
  id: string;
  team_member_id: string;
  title: string;
  organization: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
}

export interface TeamCertification {
  id: string;
  team_member_id: string;
  name: string;
  issuing_organization: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
}

export interface Client {
  id: string;
  company_id: string;
  name: string;
  industry?: string;
  website?: string;
  status: 'LEAD' | 'ACTIVE' | 'CHURNED';
  address?: string;
  notes?: string;
  is_archived: boolean;
  created_at: string;
  contacts: ClientContact[];
}

export interface ClientContact {
  id: string;
  client_id: string;
  name: string;
  email?: string;
  phone?: string;
  role?: string;
  is_primary: boolean;
}

export interface Project {
  id: string;
  company_id: string;
  client_id?: string;
  service_id?: string;
  title: string;
  description?: string;
  status: 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  contract_value: number;
  currency: string;
  start_date?: string;
  end_date?: string;
  completion_summary?: string;
  portfolio_draft_created: boolean;
  is_archived: boolean;
  created_at: string;
  team_members: Array<{ id: string; team_member_id: string; role_in_project: string }>;
  documents: Array<{ id: string; title: string; document_url: string; document_type: string; notes?: string }>;
}

export interface ServiceItem {
  id: string;
  company_id: string;
  title: string;
  category: string;
  description?: string;
  deliverables: string[];
  typical_duration?: string;
  standard_price: number;
  is_active: boolean;
  is_archived: boolean;
  created_at: string;
}

export interface AuditLog {
  id: string;
  company_id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details: Record<string, any>;
  ip_address?: string;
  created_at: string;
}

export interface PortfolioDraft {
  project_id: string;
  title: string;
  client_name?: string;
  challenge: string;
  solution: string;
  results_and_impact: string;
  technologies_used: string[];
  evidence_count: number;
  is_ready_for_review: boolean;
}
