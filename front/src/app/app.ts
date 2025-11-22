import { Sidebar } from './layout/sidebar/sidebar';
import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  WritableSignal,
  computed,
  inject,
  signal
} from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { OrgsApiService } from './services/orgs-api.service';
import {
  CollectionState,
  Cuadrilla,
  Departamento,
  Direccion,
  PaginatedResponse,
  Territorial
} from './models/orgs';

type Feedback = { type: 'success' | 'error'; text: string };

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, Sidebar],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class App implements OnInit {
  private readonly api = inject(OrgsApiService);
  private readonly fb = inject(FormBuilder);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly defaultPageSize = 10;

  protected readonly feedback = signal<Feedback | null>(null);

  protected readonly direccionesState = signal<CollectionState<Direccion>>(this.createInitialState());
  protected readonly departamentosState = signal<CollectionState<Departamento>>(this.createInitialState());
  protected readonly cuadrillasState = signal<CollectionState<Cuadrilla>>(this.createInitialState());
  protected readonly territorialesState = signal<CollectionState<Territorial>>(this.createInitialState());

  protected readonly direccionOptions = signal<Direccion[]>([]);
  protected readonly departamentoOptions = signal<Departamento[]>([]);

  protected readonly editingTerritorial = signal<Territorial | null>(null);

  protected readonly direccionFilters = this.fb.group({
    q: [''],
    estado: [''],
    responsable: ['']
  });

  protected readonly departamentoFilters = this.fb.group({
    q: [''],
    estado: [''],
    direccion: ['']
  });

  protected readonly cuadrillaFilters = this.fb.group({
    q: [''],
    estado: [''],
    departamento: ['']
  });

  protected readonly territorialFilters = this.fb.group({
    q: ['']
  });

  protected readonly direccionForm = this.fb.group({
    nombre: ['', Validators.required],
    estado: [true]
  });

  protected readonly departamentoForm = this.fb.group({
    nombre: ['', Validators.required],
    estado: [true],
    direccion: [null as number | null, Validators.required]
  });

  protected readonly cuadrillaForm = this.fb.group({
    nombre: ['', Validators.required],
    estado: [true],
    departamento: [null as number | null, Validators.required]
  });

  protected readonly territorialForm = this.fb.group({
    nombre: ['', Validators.required],
    profile: [null as number | null]
  });

  protected readonly direccionesTotalPages = computed(() =>
    this.getTotalPages(this.direccionesState().count)
  );
  protected readonly departamentosTotalPages = computed(() =>
    this.getTotalPages(this.departamentosState().count)
  );
  protected readonly cuadrillasTotalPages = computed(() =>
    this.getTotalPages(this.cuadrillasState().count)
  );
  protected readonly territorialesTotalPages = computed(() =>
    this.getTotalPages(this.territorialesState().count)
  );

  protected readonly summary = computed(() => ({
    direcciones: this.direccionesState().count,
    departamentos: this.departamentosState().count,
    cuadrillas: this.cuadrillasState().count,
    territoriales: this.territorialesState().count
  }));

  ngOnInit(): void {
    this.bootstrapData();
  }

  // ---------------------------------------------- bootstrap / fetch helpers

  protected refreshAll(): void {
    this.bootstrapData();
    this.notify('success', 'Panel actualizado correctamente.');
  }

  private bootstrapData(): void {
    this.loadDirecciones();
    this.loadDepartamentos();
    this.loadCuadrillas();
    this.loadTerritoriales();
    this.refreshReferenceData();
  }

  protected refreshReferenceData(): void {
    this.loadDireccionOptions();
    this.loadDepartamentoOptions();
  }

  private loadDireccionOptions(): void {
    this.api
      .getDirecciones({ estado: 'activa', page_size: 100 })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (response) => {
          const { items } = this.unpackResponse(response);
          this.direccionOptions.set(items);
        },
        error: () => undefined
      });
  }

  private loadDepartamentoOptions(): void {
    this.api
      .getDepartamentos({ estado: 'activo', page_size: 100 })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (response) => {
          const { items } = this.unpackResponse(response);
          this.departamentoOptions.set(items);
        },
        error: () => undefined
      });
  }

  // --------------------------------------------------------- Direcciones

protected loadDirecciones(page = this.direccionesState().page): void {
  this.startLoading(this.direccionesState);
  const filters = this.direccionFilters.value;

  this.api
    .getDirecciones({
      q: filters.q || undefined,
      estado: filters.estado || undefined,
      responsable: filters.responsable || undefined,
      page
    })
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe({
      next: (response) => {
        const { items, count } = this.unpackResponse(response);
        this.resolveState(this.direccionesState, items, page, count);
      },
      error: (error) =>
        this.failState(
          this.direccionesState,
          this.extractError(error, 'No se pudieron cargar las direcciones.')
        )
    });
}



  protected onDireccionesFilter(): void {
    this.loadDirecciones(1);
  }

  protected resetDireccionFilters(): void {
    this.direccionFilters.reset({ q: '', estado: '', responsable: '' });
    this.loadDirecciones(1);
  }

  protected submitDireccion(): void {
    if (this.direccionForm.invalid) {
      this.direccionForm.markAllAsTouched();
      return;
    }
    const payload = this.direccionForm.getRawValue();
    this.api
      .createDireccion({
        nombre: payload.nombre?.trim() ?? '',
        estado: payload.estado ?? true
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (direccion) => {
          this.notify('success', `Dirección "${direccion.nombre}" creada.`);
          this.direccionForm.reset({ nombre: '', estado: true });
          this.loadDirecciones(1);
          this.loadDireccionOptions();
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo crear la dirección.'))
      });
  }

  protected toggleDireccionEstado(direccion: Direccion): void {
    this.api
      .toggleDireccionEstado(direccion.direccion_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.notify('success', `Dirección "${updated.nombre}" actualizada.`);
          this.loadDirecciones(this.direccionesState().page);
          this.refreshReferenceData();
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo cambiar el estado.'))
      });
  }

  protected deleteDireccion(direccion: Direccion): void {
    if (!confirm(`¿Eliminar la dirección "${direccion.nombre}"?`)) {
      return;
    }
    this.api
      .deleteDireccion(direccion.direccion_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notify('success', `Dirección "${direccion.nombre}" eliminada.`);
          this.loadDirecciones(this.direccionesState().page);
          this.refreshReferenceData();
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo eliminar la dirección.'))
      });
  }

  protected changeDireccionesPage(page: number): void {
    if (page === this.direccionesState().page) {
      return;
    }
    this.loadDirecciones(page);
  }

  // --------------------------------------------------------- Departamentos

  protected loadDepartamentos(page = this.departamentosState().page): void {
  this.startLoading(this.departamentosState);
  const filters = this.departamentoFilters.value;

  this.api
    .getDepartamentos({
      q: filters.q || undefined,
      estado: filters.estado || undefined,
      direccion: filters.direccion || undefined,
      page
    })
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe({
      next: (response) => {
        const { items, count } = this.unpackResponse(response);
        this.resolveState(this.departamentosState, items, page, count);
      },
      error: (error) =>
        this.failState(
          this.departamentosState,
          this.extractError(error, 'No se pudieron cargar los departamentos.')
        )
    });
}


  protected onDepartamentosFilter(): void {
    this.loadDepartamentos(1);
  }

  protected resetDepartamentoFilters(): void {
    this.departamentoFilters.reset({ q: '', estado: '', direccion: '' });
    this.loadDepartamentos(1);
  }

  protected submitDepartamento(): void {
    if (this.departamentoForm.invalid || this.departamentoForm.value.direccion == null) {
      this.departamentoForm.markAllAsTouched();
      return;
    }
    const value = this.departamentoForm.getRawValue();
    const direccionId = Number(value.direccion);
    if (Number.isNaN(direccionId)) {
      this.notify('error', 'Selecciona una dirección válida.');
      return;
    }
    this.api
      .createDepartamento({
        nombre: value.nombre?.trim() ?? '',
        estado: value.estado ?? true,
        direccion: direccionId
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (departamento) => {
          this.notify('success', `Departamento "${departamento.nombre}" creado.`);
          this.departamentoForm.reset({ nombre: '', estado: true, direccion: null });
          this.loadDepartamentos(1);
          this.loadDepartamentoOptions();
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo crear el departamento.'))
      });
  }

  protected toggleDepartamentoEstado(departamento: Departamento): void {
    this.api
      .toggleDepartamentoEstado(departamento.departamento_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.notify('success', `Departamento "${updated.nombre}" actualizado.`);
          this.loadDepartamentos(this.departamentosState().page);
          this.refreshReferenceData();
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo cambiar el estado.'))
      });
  }

  protected deleteDepartamento(departamento: Departamento): void {
    if (!confirm(`¿Eliminar el departamento "${departamento.nombre}"?`)) {
      return;
    }
    this.api
      .deleteDepartamento(departamento.departamento_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notify('success', `Departamento "${departamento.nombre}" eliminado.`);
          this.loadDepartamentos(this.departamentosState().page);
          this.refreshReferenceData();
        },
        error: (error) =>
          this.notify(
            'error',
            this.extractError(error, 'No se pudo eliminar el departamento.')
          )
      });
  }

  protected changeDepartamentosPage(page: number): void {
    if (page === this.departamentosState().page) {
      return;
    }
    this.loadDepartamentos(page);
  }

  // --------------------------------------------------------- Cuadrillas

  protected loadCuadrillas(page = this.cuadrillasState().page): void {
  this.startLoading(this.cuadrillasState);
  const filters = this.cuadrillaFilters.value;

  this.api
    .getCuadrillas({
      q: filters.q || undefined,
      estado: filters.estado || undefined,
      departamento: filters.departamento || undefined,
      page
    })
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe({
      next: (response) => {
        const { items, count } = this.unpackResponse(response);
        this.resolveState(this.cuadrillasState, items, page, count);
      },
      error: (error) =>
        this.failState(
          this.cuadrillasState,
          this.extractError(error, 'No se pudieron cargar las cuadrillas.')
        )
    });
}


  protected onCuadrillasFilter(): void {
    this.loadCuadrillas(1);
  }

  protected resetCuadrillaFilters(): void {
    this.cuadrillaFilters.reset({ q: '', estado: '', departamento: '' });
    this.loadCuadrillas(1);
  }

  protected submitCuadrilla(): void {
    if (this.cuadrillaForm.invalid || this.cuadrillaForm.value.departamento == null) {
      this.cuadrillaForm.markAllAsTouched();
      return;
    }
    const value = this.cuadrillaForm.getRawValue();
    const departamentoId = Number(value.departamento);
    if (Number.isNaN(departamentoId)) {
      this.notify('error', 'Selecciona un departamento válido.');
      return;
    }
    this.api
      .createCuadrilla({
        nombre: value.nombre?.trim() ?? '',
        estado: value.estado ?? true,
        departamento: departamentoId
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (cuadrilla) => {
          this.notify('success', `Cuadrilla "${cuadrilla.nombre}" creada.`);
          this.cuadrillaForm.reset({ nombre: '', estado: true, departamento: null });
          this.loadCuadrillas(1);
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo crear la cuadrilla.'))
      });
  }

  protected toggleCuadrillaEstado(cuadrilla: Cuadrilla): void {
    this.api
      .toggleCuadrillaEstado(cuadrilla.cuadrilla_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.notify('success', `Cuadrilla "${updated.nombre}" actualizada.`);
          this.loadCuadrillas(this.cuadrillasState().page);
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo cambiar el estado.'))
      });
  }

  protected deleteCuadrilla(cuadrilla: Cuadrilla): void {
    if (!confirm(`¿Eliminar la cuadrilla "${cuadrilla.nombre}"?`)) {
      return;
    }
    this.api
      .deleteCuadrilla(cuadrilla.cuadrilla_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notify('success', `Cuadrilla "${cuadrilla.nombre}" eliminada.`);
          this.loadCuadrillas(this.cuadrillasState().page);
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo eliminar la cuadrilla.'))
      });
  }

  protected changeCuadrillasPage(page: number): void {
    if (page === this.cuadrillasState().page) {
      return;
    }
    this.loadCuadrillas(page);
  }

  // --------------------------------------------------------- Territoriales

  protected loadTerritoriales(page = this.territorialesState().page): void {
  this.startLoading(this.territorialesState);
  const filters = this.territorialFilters.value;

  this.api
    .getTerritoriales({
      q: filters.q || undefined,
      page
    })
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe({
      next: (response) => {
        const { items, count } = this.unpackResponse(response);
        this.resolveState(this.territorialesState, items, page, count);
      },
      error: (error) =>
        this.failState(
          this.territorialesState,
          this.extractError(error, 'No se pudieron cargar los territoriales.')
        )
    });
}

  protected onTerritorialesFilter(): void {
    this.loadTerritoriales(1);
  }

  protected resetTerritorialFilters(): void {
    this.territorialFilters.reset({ q: '' });
    this.loadTerritoriales(1);
  }

  protected submitTerritorial(): void {
    if (this.territorialForm.invalid) {
      this.territorialForm.markAllAsTouched();
      return;
    }
    const value = this.territorialForm.getRawValue();
    const profileValue = value.profile as number | string | null | undefined;
    const normalizedProfile =
      profileValue === null ||
      profileValue === undefined ||
      (typeof profileValue === 'string' && profileValue.trim() === '')
        ? null
        : Number(profileValue);

    if (normalizedProfile !== null && Number.isNaN(normalizedProfile)) {
      this.notify('error', 'El responsable debe ser un ID numérico.');
      return;
    }

    const payload = {
      nombre: value.nombre?.trim() ?? '',
      profile: normalizedProfile
    };

    const editing = this.editingTerritorial();

    const request$ = editing
      ? this.api.updateTerritorial(editing.territorial_id, payload)
      : this.api.createTerritorial(payload);

    request$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (territorial) => {
        const action = editing ? 'actualizado' : 'creado';
        this.notify('success', `Territorial "${territorial.nombre}" ${action}.`);
        this.territorialForm.reset({ nombre: '', profile: null });
        this.editingTerritorial.set(null);
        this.loadTerritoriales(editing ? this.territorialesState().page : 1);
      },
      error: (error) =>
        this.notify('error', this.extractError(error, 'No se pudo guardar el territorial.'))
    });
  }

  protected editTerritorial(territorial: Territorial): void {
    this.editingTerritorial.set(territorial);
    this.territorialForm.patchValue({
      nombre: territorial.nombre,
      profile: territorial.profile
    });
  }

  protected cancelTerritorialEdit(): void {
    this.editingTerritorial.set(null);
    this.territorialForm.reset({ nombre: '', profile: null });
  }

  protected deleteTerritorial(territorial: Territorial): void {
    if (!confirm(`¿Eliminar el territorial "${territorial.nombre}"?`)) {
      return;
    }
    this.api
      .deleteTerritorial(territorial.territorial_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notify('success', `Territorial "${territorial.nombre}" eliminado.`);
          this.loadTerritoriales(this.territorialesState().page);
        },
        error: (error) =>
          this.notify('error', this.extractError(error, 'No se pudo eliminar el territorial.'))
      });
  }

  protected changeTerritorialesPage(page: number): void {
    if (page === this.territorialesState().page) {
      return;
    }
    this.loadTerritoriales(page);
  }

  // --------------------------------------------------------- UI helpers

  protected closeFeedback(): void {
    this.feedback.set(null);
  }

  protected pageRange(total: number): number[] {
    return Array.from({ length: total }, (_, index) => index + 1);
  }

  protected trackByDireccion = (_: number, item: Direccion) => item.direccion_id;
  protected trackByDepartamento = (_: number, item: Departamento) => item.departamento_id;
  protected trackByCuadrilla = (_: number, item: Cuadrilla) => item.cuadrilla_id;
  protected trackByTerritorial = (_: number, item: Territorial) => item.territorial_id;

  protected badgeClass(isActive: boolean): string {
    return isActive ? 'is-success' : 'is-danger';
  }

  protected membershipLabel(fullName?: string | null, username?: string): string {
    return fullName?.trim() || username || 'Sin usuario';
  }

  // --------------------------------------------------------- generic helpers

  private unpackResponse<T>(response: PaginatedResponse<T> | T[]): { items: T[]; count: number } {
    if (Array.isArray(response)) {
      const items = response ?? [];
      return { items, count: items.length };
    }
    const items = response?.results ?? [];
    const count =
      typeof response?.count === 'number' && !Number.isNaN(response.count)
        ? response.count
        : items.length;
    return { items, count };
  }

  private createInitialState<T>(): CollectionState<T> {
    return { items: [], count: 0, loading: false, error: null, page: 1 };
  }

  private startLoading<T>(state: WritableSignal<CollectionState<T>>): void {
    state.update((current) => ({ ...current, loading: true, error: null }));
  }

  private resolveState<T>(
    state: WritableSignal<CollectionState<T>>,
    items: T[],
    page: number,
    count?: number
  ): void {
    state.set({
      items: items || [],
      count: count ?? items?.length ?? 0,
      loading: false,
      error: null,
      page
    });
  }

  private failState<T>(state: WritableSignal<CollectionState<T>>, message: string): void {
    state.update((current) => ({ ...current, loading: false, error: message }));
  }

  private getTotalPages(count: number): number {
    return Math.max(1, Math.ceil(count / this.defaultPageSize));
  }

  private notify(type: 'success' | 'error', text: string): void {
    this.feedback.set({ type, text });
  }

  private extractError(error: unknown, fallback: string): string {
    const detail = (error as { error?: unknown })?.error;
    if (!detail) {
      return fallback;
    }
    if (typeof detail === 'string') {
      return detail;
    }
    const detailRecord = detail as Record<string, unknown>;
    if (detailRecord['detail']) {
      const value = detailRecord['detail'];
      return typeof value === 'string' ? value : fallback;
    }
    if (Array.isArray(detail)) {
      return detail.join(', ');
    }
    return fallback;
  }
}
