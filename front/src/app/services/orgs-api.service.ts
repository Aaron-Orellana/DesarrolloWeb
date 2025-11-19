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

  getDirecciones(params: DireccionFilters = {}): Observable<PaginatedResponse<Direccion>> {
    return this.requestPaginated<Direccion>('direcciones', params);
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

  getDepartamentos(params: DepartamentoFilters = {}): Observable<PaginatedResponse<Departamento>> {
    return this.requestPaginated<Departamento>('departamentos', params);
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

  getCuadrillas(params: CuadrillaFilters = {}) {
    return this.requestPaginated<Cuadrilla>('cuadrillas', params);
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

  getTerritoriales(params: TerritorialFilters = {}) {
    return this.requestPaginated<Territorial>('territoriales', params);
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

  private requestPaginated<T>(
    endpoint: string,
    params: Record<string, string | number | boolean | undefined> = {}
  ) {
    return this.http.get<PaginatedResponse<T>>(`${API_BASE_URL}/${endpoint}/`, {
      params: this.buildParams(params)
    });
  }

  private buildParams(params: Record<string, string | number | boolean | undefined>) {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') {
        return;
      }
      httpParams = httpParams.set(key, String(value));
    });
    return httpParams;
  }
}
