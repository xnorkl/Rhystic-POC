export class SignalingClient {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.ws = null;
        this.messageHandlers = new Map();
    }

    connect(roomId) {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(`${this.serverUrl}/ws?room=${roomId}`);
            
            this.ws.onopen = () => resolve();
            this.ws.onerror = (error) => reject(error);
            this.ws.onmessage = (event) => this.#handleMessage(JSON.parse(event.data));
        });
    }

    on(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    #handleMessage(message) {
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            handler(message);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}