package com.remotedesktop

import org.junit.Assert.*
import org.junit.Test
import org.json.JSONObject

class InputForwarderTest {
    @Test
    fun `buildMouseMove normaliza coordenadas para 0-1`() {
        val json = InputForwarder.buildMouseMove(
            touchX = 480f, touchY = 270f,
            viewWidth = 960f, viewHeight = 540f
        )
        val obj = JSONObject(json)
        assertEquals("mouse_move", obj.getString("type"))
        assertEquals(0.5, obj.getDouble("x"), 0.001)
        assertEquals(0.5, obj.getDouble("y"), 0.001)
    }

    @Test
    fun `buildMouseMove clamp nao passa de 1`() {
        val json = InputForwarder.buildMouseMove(960f, 540f, 960f, 540f)
        val obj = JSONObject(json)
        assertTrue(obj.getDouble("x") <= 1.0)
        assertTrue(obj.getDouble("y") <= 1.0)
    }

    @Test
    fun `buildMouseClick retorna JSON correto`() {
        val json = InputForwarder.buildMouseClick("left")
        val obj = JSONObject(json)
        assertEquals("mouse_click", obj.getString("type"))
        assertEquals("left", obj.getString("button"))
    }

    @Test
    fun `buildKeyType retorna JSON correto`() {
        val json = InputForwarder.buildKeyType("hello")
        val obj = JSONObject(json)
        assertEquals("key_type", obj.getString("type"))
        assertEquals("hello", obj.getString("text"))
    }
}
