package com.remotedesktop

import android.content.Context
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputConnection
import org.webrtc.EglBase
import org.webrtc.SurfaceViewRenderer
import org.webrtc.VideoTrack

class RemoteSurfaceView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : SurfaceViewRenderer(context, attrs) {

    var inputForwarder: InputForwarder? = null

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val fwd = inputForwarder ?: return super.onTouchEvent(event)
        when (event.action) {
            MotionEvent.ACTION_MOVE -> fwd.onTouch(event.x, event.y, width.toFloat(), height.toFloat())
            MotionEvent.ACTION_UP -> {
                fwd.onTouch(event.x, event.y, width.toFloat(), height.toFloat())
                fwd.onClick("left")
            }
        }
        return true
    }

    override fun onCheckIsTextEditor() = true

    override fun onCreateInputConnection(outAttrs: EditorInfo): InputConnection? {
        outAttrs.inputType = android.text.InputType.TYPE_CLASS_TEXT
        return object : android.view.inputmethod.BaseInputConnection(this, false) {
            override fun commitText(text: CharSequence?, newCursorPosition: Int): Boolean {
                inputForwarder?.onKeyboardText(text.toString())
                return true
            }
        }
    }
}
