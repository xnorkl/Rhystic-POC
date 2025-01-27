export class WebRTCClient {
    constructor(signaling, config) {
        this.signaling = signaling;
        this.peerConnection = null;
        this.config = config;
        this.localStream = null;
        this.onTrack = null;
    }

    async initialize() {
        this.peerConnection = new RTCPeerConnection(this.config);
        
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.signaling.send({
                    type: 'ice',
                    candidate: event.candidate
                });
            }
        };

        this.peerConnection.ontrack = (event) => {
            if (this.onTrack) {
                this.onTrack(event.streams[0]);
            }
        };

        this.#setupSignalingHandlers();
    }

    async startLocalStream() {
        this.localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });

        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });

        return this.localStream;
    }

    #setupSignalingHandlers() {
        this.signaling.on('offer', async (message) => {
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp));
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            
            this.signaling.send({
                type: 'answer',
                sdp: answer
            });
        });

        this.signaling.on('answer', async (message) => {
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp));
        });

        this.signaling.on('ice', async (message) => {
            try {
                await this.peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            } catch (e) {
                console.error('Error adding received ice candidate', e);
            }
        });
    }

    async createOffer() {
        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);
        
        this.signaling.send({
            type: 'offer',
            sdp: offer
        });
    }

    dispose() {
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }
        if (this.peerConnection) {
            this.peerConnection.close();
        }
    }
}