import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import {
  Cuadrilla,
  CuadrillaFilters,
  Departamento,
  DepartamentoFilters,
  Direccion,
  DireccionFilters,
  PaginatedResponse,
  Territorial,
  TerritorialFilters
} from '../models/orgs';

const API_BASE_URL = 'http://localhost:8000/api/orgs';

@Injectable({
  providedIn: 'root'
})
export class OrgsApiService {
  private readonly http = inject(HttpClient);

  // -------------------------- DIRECCIONES --------------------------
  getDirecciones(params: DireccionFilters = {}): Observable<PaginatedResponse<Direccion>> {
    return this.http.get<PaginatedResponse<Direccion>>(`${API_BASE_URL}/direcciones/`, {
      params: this.buildParams(params)
    });
  }

  createDireccion(payload: Pick<Direccion, 'nombre' | 'estado'>) {
    return this.http.post<Direccion>(`${API_BASE_URL}/direcciones/`, payload);
  }

  toggleDireccionEstado(id: number) {
    return this.http.post<Direccion>(`${API_BASE_URL}/direcciones/${id}/toggle-estado/`, {});
  }

  deleteDireccion(id: number) {
    return this.http.delete(`${API_BASE_URL}/direcciones/${id}/`);
  }

  // -------------------------- DEPARTAMENTOS --------------------------
  getDepartamentos(
    params: DepartamentoFilters = {}
  ): Observable<PaginatedResponse<Departamento>> {
    return this.http.get<PaginatedResponse<Departamento>>(`${API_BASE_URL}/departamentos/`, {
      params: this.buildParams(params)
    });
  }

  createDepartamento(payload: { nombre: string; estado: boolean; direccion: number }) {
    return this.http.post<Departamento>(`${API_BASE_URL}/departamentos/`, payload);
  }

  toggleDepartamentoEstado(id: number) {
    return this.http.post<Departamento>(
      `${API_BASE_URL}/departamentos/${id}/toggle-estado/`,
      {}
    );
  }

  deleteDepartamento(id: number) {
    return this.http.delete(`${API_BASE_URL}/departamentos/${id}/`);
  }

  // -------------------------- CUADRILLAS --------------------------
  getCuadrillas(params: CuadrillaFilters = {}): Observable<PaginatedResponse<Cuadrilla>> {
    return this.http.get<PaginatedResponse<Cuadrilla>>(`${API_BASE_URL}/cuadrillas/`, {
      params: this.buildParams(params)
    });
  }

  createCuadrilla(payload: { nombre: string; estado: boolean; departamento: number }) {
    return this.http.post<Cuadrilla>(`${API_BASE_URL}/cuadrillas/`, payload);
  }

  toggleCuadrillaEstado(id: number) {
    return this.http.post<Cuadrilla>(`${API_BASE_URL}/cuadrillas/${id}/toggle-estado/`, {});
  }

  deleteCuadrilla(id: number) {
    return this.http.delete(`${API_BASE_URL}/cuadrillas/${id}/`);
  }

  // -------------------------- TERRITORIALES --------------------------
  getTerritoriales(
    params: TerritorialFilters = {}
  ): Observable<PaginatedResponse<Territorial>> {
    return this.http.get<PaginatedResponse<Territorial>>(`${API_BASE_URL}/territoriales/`, {
      params: this.buildParams(params)
    });
  }

  createTerritorial(payload: { nombre: string; profile: number | null }) {
    return this.http.post<Territorial>(`${API_BASE_URL}/territoriales/`, payload);
  }

  updateTerritorial(id: number, payload: { nombre: string; profile: number | null }) {
    return this.http.patch<Territorial>(`${API_BASE_URL}/territoriales/${id}/`, payload);
  }

  deleteTerritorial(id: number) {
    return this.http.delete(`${API_BASE_URL}/territoriales/${id}/`);
  }

  // -------------------------- HELPERS --------------------------
  private buildParams(params: Record<string, string | number | boolean | undefined>) {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') return;
      httpParams = httpParams.set(key, String(value));
    });
    return httpParams;
  }
}
