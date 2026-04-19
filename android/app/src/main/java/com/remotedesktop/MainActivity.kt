package com.remotedesktop

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import org.webrtc.VideoTrack

class MainActivity : AppCompatActivity() {

    // ⚠️ Substituir pela URL real do servidor Render.com após deploy (Task 10)
    private val SIGNALING_URL = "https://SEU-APP.onrender.com"
    private val ROOM_ID = "meu-desktop"

    private lateinit var remoteView: RemoteSurfaceView
    private lateinit var webRTCManager: WebRTCManager
    private lateinit var signalingClient: SignalingClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        remoteView = findViewById(R.id.remoteView)

        signalingClient = SignalingClient(
            serverUrl = SIGNALING_URL,
            roomId = ROOM_ID,
            listener = object : SignalingClient.Listener {
                override fun onOffer(sdp: org.webrtc.SessionDescription) = webRTCManager.onOffer(sdp)
                override fun onAnswer(sdp: org.webrtc.SessionDescription) = webRTCManager.onAnswer(sdp)
                override fun onIceCandidate(candidate: org.webrtc.IceCandidate) = webRTCManager.onIceCandidate(candidate)
                override fun onPeerReady() = webRTCManager.onPeerReady()
            }
        )

        webRTCManager = WebRTCManager(
            context = this,
            signalingClient = signalingClient,
            onDataChannelOpen = { dc ->
                val forwarder = InputForwarder(dc)
                runOnUiThread { remoteView.inputForwarder = forwarder }
            },
            onVideoTrack = { track: VideoTrack ->
                runOnUiThread {
                    remoteView.init(webRTCManager.getEglBase().eglBaseContext, null)
                    remoteView.setEnableHardwareScaler(true)
                    track.addSink(remoteView)
                }
            }
        )

        webRTCManager.start()
    }

    override fun onDestroy() {
        super.onDestroy()
        signalingClient.disconnect()
        webRTCManager.close()
        remoteView.release()
    }
}
