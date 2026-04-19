package com.remotedesktop

import org.json.JSONObject
import org.webrtc.DataChannel
import java.nio.ByteBuffer

class InputForwarder(private val dataChannel: DataChannel?) {

    fun onTouch(touchX: Float, touchY: Float, viewWidth: Float, viewHeight: Float) {
        send(buildMouseMove(touchX, touchY, viewWidth, viewHeight))
    }

    fun onClick(button: String = "left") {
        send(buildMouseClick(button))
    }

    fun onScroll(dx: Float, dy: Float) {
        send(JSONObject().apply {
            put("type", "mouse_scroll")
            put("dx", dx.toDouble())
            put("dy", dy.toDouble())
        }.toString())
    }

    fun onKeyboardText(text: String) {
        send(buildKeyType(text))
    }

    private fun send(json: String) {
        val dc = dataChannel ?: return
        if (dc.state() != DataChannel.State.OPEN) return
        val bytes = json.toByteArray(Charsets.UTF_8)
        dc.send(DataChannel.Buffer(ByteBuffer.wrap(bytes), false))
    }

    companion object {
        fun buildMouseMove(touchX: Float, touchY: Float, viewWidth: Float, viewHeight: Float): String {
            val x = (touchX / viewWidth).coerceIn(0f, 1f).toDouble()
            val y = (touchY / viewHeight).coerceIn(0f, 1f).toDouble()
            return JSONObject().apply {
                put("type", "mouse_move")
                put("x", x)
                put("y", y)
            }.toString()
        }

        fun buildMouseClick(button: String): String =
            JSONObject().apply {
                put("type", "mouse_click")
                put("button", button)
            }.toString()

        fun buildKeyType(text: String): String =
            JSONObject().apply {
                put("type", "key_type")
                put("text", text)
            }.toString()
    }
}
