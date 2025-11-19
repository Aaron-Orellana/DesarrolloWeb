export interface ProfileSummary {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role_type: string | null;
}

export interface DireccionMembership {
  direccion_membership_id: number;
  usuario: ProfileSummary | null;
  es_encargado: boolean;
  desde: string;
}

export interface DepartamentoMembership {
  departamento_membership_id: number;
  usuario: ProfileSummary | null;
  es_encargado: boolean;
  desde: string;
}

export interface CuadrillaMembership {
  cuadrilla_membership_id: number;
  usuario: ProfileSummary | null;
  desde: string;
}

export interface Direccion {
  direccion_id: number;
  nombre: string;
  estado: boolean;
  memberships: DireccionMembership[];
}

export interface DireccionSummary {
  direccion_id: number;
  nombre: string;
  estado: boolean;
}

export interface Departamento {
  departamento_id: number;
  nombre: string;
  estado: boolean;
  direccion: number;
  direccion_detalle?: DireccionSummary | null;
  memberships: DepartamentoMembership[];
}

export interface DepartamentoSummary {
  departamento_id: number;
  nombre: string;
  estado: boolean;
  direccion?: DireccionSummary | null;
}

export interface Cuadrilla {
  cuadrilla_id: number;
  nombre: string;
  estado: boolean;
  departamento: number;
  departamento_detalle?: DepartamentoSummary | null;
  memberships: CuadrillaMembership[];
}

export interface Territorial {
  territorial_id: number;
  nombre: string;
  profile: number | null;
  profile_detalle: ProfileSummary | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CollectionState<T> {
  items: T[];
  count: number;
  loading: boolean;
  error: string | null;
  page: number;
}

type FilterParams = Record<string, string | number | boolean | undefined>;

export type DireccionFilters = FilterParams & {
  q?: string;
  estado?: string;
  responsable?: string;
  page?: number;
  page_size?: number;
};

export type DepartamentoFilters = FilterParams & {
  q?: string;
  estado?: string;
  direccion?: string | number;
  page?: number;
  page_size?: number;
};

export type CuadrillaFilters = FilterParams & {
  q?: string;
  estado?: string;
  departamento?: string | number;
  page?: number;
  page_size?: number;
};

export type TerritorialFilters = FilterParams & {
  q?: string;
  page?: number;
  page_size?: number;
};
