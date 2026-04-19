package com.remotedesktop

import org.junit.Assert.*
import org.junit.Test

class SignalingClientTest {
    @Test
    fun `parseCandidate retorna null para candidate vazio`() {
        val result = SignalingClient.parseCandidate(
            mapOf("candidate" to "", "sdpMid" to "0", "sdpMLineIndex" to 0)
        )
        assertNull(result)
    }

    @Test
    fun `parseCandidate retorna candidato para dados validos`() {
        val result = SignalingClient.parseCandidate(
            mapOf(
                "candidate" to "candidate:1 1 UDP 2130706431 192.168.1.1 50000 typ host",
                "sdpMid" to "0",
                "sdpMLineIndex" to 0
            )
        )
        assertNotNull(result)
        assertEquals("0", result?.sdpMid)
    }
}
