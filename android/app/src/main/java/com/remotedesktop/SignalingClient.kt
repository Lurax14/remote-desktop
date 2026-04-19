package com.remotedesktop

import io.socket.client.IO
import io.socket.client.Socket
import org.json.JSONObject
import org.webrtc.IceCandidate
import org.webrtc.SessionDescription

class SignalingClient(
    private val serverUrl: String,
    private val roomId: String,
    private val listener: Listener
) {
    interface Listener {
        fun onOffer(sdp: SessionDescription)
        fun onAnswer(sdp: SessionDescription)
        fun onIceCandidate(candidate: IceCandidate)
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
            listener.onOffer(
                SessionDescription(SessionDescription.Type.OFFER, obj.getString("sdp"))
            )
        }

        socket.on("answer") { args ->
            val obj = args[0] as JSONObject
            listener.onAnswer(
                SessionDescription(SessionDescription.Type.ANSWER, obj.getString("sdp"))
            )
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

    fun sendOffer(sdp: SessionDescription) {
        val obj = JSONObject().apply {
            put("roomId", roomId)
            put("sdp", JSONObject().apply {
                put("type", sdp.type.canonicalForm())
                put("sdp", sdp.description)
            })
        }
        socket.emit("offer", obj)
    }

    fun sendAnswer(sdp: SessionDescription) {
        val obj = JSONObject().apply {
            put("roomId", roomId)
            put("sdp", JSONObject().apply {
                put("type", sdp.type.canonicalForm())
                put("sdp", sdp.description)
            })
        }
        socket.emit("answer", obj)
    }

    fun sendIceCandidate(candidate: IceCandidate) {
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
        fun parseCandidate(map: Map<String, Any?>): IceCandidate? {
            val sdp = map["candidate"] as? String ?: return null
            if (sdp.isBlank()) return null
            return IceCandidate(
                map["sdpMid"] as? String ?: "0",
                (map["sdpMLineIndex"] as? Int) ?: 0,
                sdp
            )
        }
    }
}
