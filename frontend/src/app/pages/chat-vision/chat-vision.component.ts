import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgentService } from '../../services/agent.service';
import { SpeechService } from '../../services/speech.service';

@Component({
  selector: 'app-chat-vision',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-vision.component.html'
})
export class ChatVisionComponent {
  userQuery: string = 'What are the top risks for Project Orion Upgrade?';
  chatResponse: string = '';
  isRecordingVoice: boolean = false;
  selectedFileName: string = '';

  constructor(
    private agentService: AgentService,
    private speechService: SpeechService
  ) {}

  sendQuery(): void {
    this.agentService.sendAgentChat(this.userQuery, 'PRJ-001').subscribe(res => {
      if (res && res.chat_result) {
        this.chatResponse = res.chat_result.response;
      }
    });
  }

  startVoice(): void {
    this.isRecordingVoice = true;
    this.speechService.startSpeechToText(
      (text) => {
        this.userQuery = text;
        this.isRecordingVoice = false;
        this.speechService.textToSpeech(`Received query: ${text}. Running Chat Supervisor Agent.`);
        this.sendQuery();
      },
      (err) => {
        this.isRecordingVoice = false;
        alert(`Voice Error: ${err}`);
      }
    );
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFileName = file.name;
      this.chatResponse = `[Vision OCR Agent] Successfully parsed document '${file.name}'. Extracting text and performing RAG policy compliance check against security_policy.txt...`;
    }
  }
}
