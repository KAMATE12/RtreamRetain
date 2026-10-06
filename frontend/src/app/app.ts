import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { finalize } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private readonly http = inject(HttpClient);
  readonly api = signal('Not checked');
  readonly database = signal('Not checked');
  readonly checking = signal(false);

  checkConnections(): void {
    this.checking.set(true);
    this.api.set('Checking…');
    this.database.set('Checking…');
    this.http.get<{status: string}>('/api/health').subscribe({
      next: () => this.api.set('Connected'),
      error: () => this.api.set('Unavailable — start the backend')
    });
    this.http.get<{database: string}>('/api/readiness')
      .pipe(finalize(() => this.checking.set(false)))
      .subscribe({
        next: () => this.database.set('Connected'),
        error: () => this.database.set('Not ready — check the API and PostgreSQL')
      });
  }
}
