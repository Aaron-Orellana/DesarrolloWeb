import { Component } from '@angular/core';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {
  // cuál sección está activa
  current: 'direcciones' | 'departamentos' | 'cuadrillas' | 'territoriales' = 'direcciones';

  go(section: 'direcciones' | 'departamentos' | 'cuadrillas' | 'territoriales'): void {
    // marcar el botón activo
    this.current = section;

    // buscar el elemento por id en la página
    if (typeof document !== 'undefined') {
      const el = document.getElementById(section);
      if (el) {
        el.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  }
}

