import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {
  private readonly sections = ['direcciones', 'departamentos', 'cuadrillas', 'territoriales'] as const;
  // sección activa para resaltar el link
  current: (typeof this.sections)[number] = 'direcciones';
  scrollDirection: 'up' | 'down' | null = null;
  private hintTimeoutId: ReturnType<typeof setTimeout> | null = null;

  go(event: Event, section: (typeof this.sections)[number]): void {
    event.preventDefault();
    this.current = section;

    // buscar el elemento por id en la página
    if (typeof document !== 'undefined') {
      const el = document.getElementById(section);
      if (el) {
        const currentOffset = window.scrollY || document.documentElement.scrollTop || 0;
        const targetOffset = currentOffset + el.getBoundingClientRect().top;
        this.showDirectionHint(targetOffset, currentOffset);
        el.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  }

  private showDirectionHint(targetOffset: number, currentOffset: number): void {
    const delta = targetOffset - currentOffset;
    if (Math.abs(delta) < 8) {
      this.scrollDirection = null;
      return;
    }
    this.scrollDirection = delta > 0 ? 'down' : 'up';
    if (this.hintTimeoutId) {
      clearTimeout(this.hintTimeoutId);
    }
    this.hintTimeoutId = setTimeout(() => {
      this.scrollDirection = null;
      this.hintTimeoutId = null;
    }, 1200);
  }
}
