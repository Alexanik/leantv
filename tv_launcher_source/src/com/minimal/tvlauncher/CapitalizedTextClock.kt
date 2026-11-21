package com.minimal.tvlauncher

import android.content.Context
import android.util.AttributeSet
import android.widget.TextClock
import java.util.Locale

class CapitalizedTextClock @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : TextClock(context, attrs, defStyleAttr) {

    override fun setText(text: CharSequence?, type: BufferType?) {
        val str = text?.toString()
        if (!str.isNullOrEmpty()) {
            val capitalized = str.substring(0, 1).uppercase(Locale.getDefault()) + str.substring(1)
            super.setText(capitalized, type)
        } else {
            super.setText(text, type)
        }
    }
}
