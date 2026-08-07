import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-implementation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './implementation.component.html'
})
export class ImplementationComponent {
  selectedProjectCode: string = 'PRJ-001';
}
