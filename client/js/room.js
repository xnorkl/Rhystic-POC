export class RoomClient {
    constructor(signaling, webrtc) {
        this.signaling = signaling;
        this.webrtc = webrtc;
        this.peers = new Map();
    }

    async joinRoom(roomId) {
        try {
            await this.signaling.connect(roomId);
            await this.webrtc.initialize();
            const localStream = await this.webrtc.startLocalStream();
            
            this.signaling.on('peer_joined', (message) => {
                this.#handlePeerJoined(message.peerId);
            });

            this.signaling.on('peer_left', (message) => {
                this.#handlePeerLeft(message.peerId);
            });

            return localStream;
        } catch (error) {
            console.error('Error joining room:', error);
            throw error;
        }
    }

    #handlePeerJoined(peerId) {
        this.peers.set(peerId, {
            id: peerId,
            stream: null
        });
        this.webrtc.createOffer();
    }

    #handlePeerLeft(peerId) {
        this.peers.delete(peerId);
    }

    leaveRoom() {
        this.webrtc.dispose();
        this.signaling.disconnect();
        this.peers.clear();
    }
}