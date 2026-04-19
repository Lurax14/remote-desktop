package com.remotedesktop

import io.socket.client.IO
import io.socket.client.Socket
import org.json.JSONObject

// Lightweight data class used instead of org.webrtc.IceCandidate so that
// companion-object logic is testable on the JVM without the Android AAR.
data class IceCandidateData(val sdpMid: String, val sdpMLineIndex: Int, val sdp: String)

class SignalingClient(
    private val serverUrl: String,
    private val roomId: String,
    private val listener: Listener
) {
    interface Listener {
        fun onOffer(sdpType: String, sdpDescription: String)
        fun onAnswer(sdpType: String, sdpDescription: String)
        fun onIceCandidate(candidate: IceCandidateData)
        fun onPeerReady()
    }

    private val socket: Socket = IO.socket(serverUrl)

    fun connect() {
        socket.on(Socket.EVENT_CONNECT) {
            socket.emit("join", roomId)
        }

        socket.on("peer-ready") {
            listener.onPeerReady()
        }

        socket.on("offer") { args ->
            val obj = args[0] as JSONObject
            listener.onOffer("offer", obj.getString("sdp"))
        }

        socket.on("answer") { args ->
            val obj = args[0] as JSONObject
            listener.onAnswer("answer", obj.getString("sdp"))
        }

        socket.on("ice-candidate") { args ->
            val obj = args[0] as JSONObject
            parseCandidate(
                mapOf(
                    "candidate" to obj.optString("candidate"),
                    "sdpMid" to obj.optString("sdpMid"),
                    "sdpMLineIndex" to obj.optInt("sdpMLineIndex")
                )
            )?.let { listener.onIceCandidate(it) }
        }

        socket.connect()
    }

    fun sendOffer(sdpType: String, sdpDescription: String) {
        val obj = JSONObject().apply {
            put("roomId", roomId)
            put("sdp", JSONObject().apply {
                put("type", sdpType)
                put("sdp", sdpDescription)
            })
        }
        socket.emit("offer", obj)
    }

    fun sendAnswer(sdpType: String, sdpDescription: String) {
        val obj = JSONObject().apply {
            put("roomId", roomId)
            put("sdp", JSONObject().apply {
                put("type", sdpType)
                put("sdp", sdpDescription)
            })
        }
        socket.emit("answer", obj)
    }

    fun sendIceCandidate(candidate: IceCandidateData) {
        val obj = JSONObject().apply {
            put("roomId", roomId)
            put("candidate", JSONObject().apply {
                put("candidate", candidate.sdp)
                put("sdpMid", candidate.sdpMid)
                put("sdpMLineIndex", candidate.sdpMLineIndex)
            })
        }
        socket.emit("ice-candidate", obj)
    }

    fun disconnect() = socket.disconnect()

    companion object {
        fun parseCandidate(map: Map<String, Any?>): IceCandidateData? {
            val sdp = map["candidate"] as? String ?: return null
            if (sdp.isBlank()) return null
            return IceCandidateData(
                sdpMid = map["sdpMid"] as? String ?: "0",
                sdpMLineIndex = (map["sdpMLineIndex"] as? Int) ?: 0,
                sdp = sdp
            )
        }
    }
}
