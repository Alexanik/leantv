package com.minimal.tvlauncher

import android.app.Activity
import android.app.AlertDialog
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.content.pm.ResolveInfo
import android.graphics.drawable.Drawable
import android.media.tv.TvContract
import android.media.tv.TvInputInfo
import android.media.tv.TvInputManager
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.util.TypedValue
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextClock
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {

    companion object {
        private const val PREFS_NAME = "minimal_launcher_prefs"
        private const val KEY_APPS_ORDER = "apps_order"
        private const val KEY_HIDDEN_APPS = "hidden_apps"
        private const val KEY_INPUTS_ORDER = "inputs_order"
        private const val KEY_HIDDEN_INPUTS = "hidden_inputs"
        private const val KEY_CLOCK_SIZE_MODE = "clock_size_mode"

        private const val TAG_TYPE_APP = "app:"
        private const val TAG_TYPE_INPUT = "input:"
    }

    data class InputDef(
        val id: String,
        val title: String,
        val iconRes: Int,
        val uriOrAction: String,
        val isAction: Boolean = false
    )

    private var allInputs: List<InputDef> = emptyList()
    private var tvInputManager: TvInputManager? = null
    private val tvInputCallback = object : TvInputManager.TvInputCallback() {
        override fun onInputAdded(inputId: String) {
            runOnUiThread { loadInputs() }
        }
        override fun onInputRemoved(inputId: String) {
            runOnUiThread { loadInputs() }
        }
        override fun onInputUpdated(inputId: String) {
            runOnUiThread { loadInputs() }
        }
        override fun onInputStateChanged(inputId: String, state: Int) {
            runOnUiThread { loadInputs() }
        }
    }

    private val packageReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            runOnUiThread { loadInstalledApps() }
        }
    }

    private lateinit var prefs: SharedPreferences
    private lateinit var clockView: TextClock
    private lateinit var dateView: TextClock
    private lateinit var btnSettings: FrameLayout
    private lateinit var inputsContainer: LinearLayout
    private lateinit var appsContainer: LinearLayout

    // Clock size mode: 0 = Standard (56sp), 1 = Large (88sp), 2 = Huge (116sp)
    private var clockSizeMode = 0

    // Move Mode state
    private var isMoveMode = false
    private var movingView: View? = null
    private var movingContainer: LinearLayout? = null
    private var waitingForInitialOkRelease = false

    // Long press detection
    private val dpadHandler = Handler(Looper.getMainLooper())
    private var isDpadCenterDown = false
    private var handledAsLongPress = false
    private var dpadTargetView: View? = null

    private var currentAllInstalledApps = mutableListOf<ResolveInfo>()
    private var currentAppsOrder = mutableListOf<String>()
    private var currentInputsOrder = mutableListOf<String>()

    private val enterMoveModeRunnable = Runnable {
        if (isDpadCenterDown && dpadTargetView != null) {
            handledAsLongPress = true
            enterMoveMode(dpadTargetView!!)
        }
    }

    private val openHiddenManagerRunnable = Runnable {
        if (isDpadCenterDown && dpadTargetView != null) {
            handledAsLongPress = true
            val target = dpadTargetView
            val tag = target?.tag as? String ?: ""
            exitMoveMode(false)
            if (tag.startsWith(TAG_TYPE_INPUT)) {
                showHiddenInputsDialog()
            } else if (tag.startsWith(TAG_TYPE_APP)) {
                showHiddenAppsDialog()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        clockView = findViewById(R.id.clock)
        dateView = findViewById(R.id.date)
        btnSettings = findViewById(R.id.btn_settings)
        inputsContainer = findViewById(R.id.inputs_container)
        appsContainer = findViewById(R.id.apps_container)

        // Setup Clock Mode (saved in prefs, controlled from Settings menu)
        clockSizeMode = prefs.getInt(KEY_CLOCK_SIZE_MODE, 0)
        applyClockSize()

        // Setup Settings Button (Icon only, 50% alpha at rest, 100% on focus, no box)
        btnSettings.setOnFocusChangeListener { v, hasFocus ->
            if (hasFocus) {
                v.animate().scaleX(1.15f).scaleY(1.15f).alpha(1.0f).setDuration(120).start()
            } else {
                v.animate().scaleX(0.95f).scaleY(0.95f).alpha(0.5f).setDuration(120).start()
            }
        }
        btnSettings.setOnClickListener {
            showSettingsMenu()
        }

        try {
            tvInputManager = getSystemService(Context.TV_INPUT_SERVICE) as? TvInputManager
            tvInputManager?.registerCallback(tvInputCallback, dpadHandler)
        } catch (e: Exception) {
            // Ignore
        }

        try {
            val packageFilter = IntentFilter().apply {
                addAction(Intent.ACTION_PACKAGE_ADDED)
                addAction(Intent.ACTION_PACKAGE_REMOVED)
                addAction(Intent.ACTION_PACKAGE_REPLACED)
                addDataScheme("package")
            }
            registerReceiver(packageReceiver, packageFilter)
        } catch (e: Exception) {
            // Ignore
        }

        loadInputs()
        loadInstalledApps()

        // Focus first visible input or app
        if (inputsContainer.childCount > 0) {
            inputsContainer.getChildAt(0).requestFocus()
        } else if (appsContainer.childCount > 0) {
            appsContainer.getChildAt(0).requestFocus()
        } else {
            btnSettings.requestFocus()
        }
    }

    override fun onResume() {
        super.onResume()
        if (!isMoveMode) {
            loadInputs()
            loadInstalledApps()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            tvInputManager?.unregisterCallback(tvInputCallback)
        } catch (e: Exception) {
            // Ignore
        }
        try {
            unregisterReceiver(packageReceiver)
        } catch (e: Exception) {
            // Ignore
        }
        dpadHandler.removeCallbacksAndMessages(null)
    }

    private fun applyClockSize() {
        when (clockSizeMode) {
            1 -> {
                clockView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 88f)
                dateView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f)
            }
            2 -> {
                clockView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 116f)
                dateView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24f)
            }
            else -> {
                clockView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 56f)
                dateView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
            }
        }
    }

    private fun showSettingsMenu() {
        val items = arrayOf(
            getString(R.string.settings_tv),
            getString(R.string.settings_hidden_apps),
            getString(R.string.settings_hidden_inputs),
            getString(R.string.settings_clock_size)
        )
        AlertDialog.Builder(this, AlertDialog.THEME_DEVICE_DEFAULT_DARK)
            .setTitle(getString(R.string.settings))
            .setItems(items) { _, which ->
                when (which) {
                    0 -> {
                        try {
                            startActivity(Intent(Settings.ACTION_SETTINGS))
                        } catch (e: Exception) {
                            Toast.makeText(this, getString(R.string.settings_open_error), Toast.LENGTH_SHORT).show()
                        }
                    }
                    1 -> showHiddenAppsDialog()
                    2 -> showHiddenInputsDialog()
                    3 -> showClockSizeDialog()
                }
            }
            .show()
    }

    private fun showClockSizeDialog() {
        val options = arrayOf(
            getString(R.string.clock_size_standard),
            getString(R.string.clock_size_large),
            getString(R.string.clock_size_huge)
        )
        AlertDialog.Builder(this, AlertDialog.THEME_DEVICE_DEFAULT_DARK)
            .setTitle(getString(R.string.settings_clock_size))
            .setSingleChoiceItems(options, clockSizeMode) { dialog, which ->
                clockSizeMode = which
                applyClockSize()
                prefs.edit().putInt(KEY_CLOCK_SIZE_MODE, clockSizeMode).apply()
                dialog.dismiss()
            }
            .setNegativeButton(getString(R.string.btn_cancel), null)
            .show()
    }

    // =========================================================================
    // Inputs Loading & Handling
    // =========================================================================

    private fun discoverTvInputs(): List<InputDef> {
        val list = mutableListOf<InputDef>()
        try {
            val tvInputManager = getSystemService(Context.TV_INPUT_SERVICE) as? TvInputManager
            val rawList = tvInputManager?.tvInputList ?: emptyList()

            // 1. Add Tuner / Cable / Antenna TV if available
            val tunerInputs = rawList.filter { it.type == TvInputInfo.TYPE_TUNER && it.parentId == null }
            for (info in tunerInputs) {
                val custom = try { info.loadCustomLabel(this)?.toString() } catch (e: Exception) { null }
                val defaultLabel = try { info.loadLabel(this)?.toString() } catch (e: Exception) { null }
                val label = if (!custom.isNullOrBlank()) custom else if (!defaultLabel.isNullOrBlank()) defaultLabel else getString(R.string.input_tuner)
                val uri = TvContract.buildChannelUriForPassthroughInput(info.id).toString()
                list.add(InputDef(info.id, label, R.drawable.ic_inputs, uri, isAction = false))
            }

            // 2. Physical external hardware inputs (HDMI, AV, Composite, Component)
            val passthroughList = rawList.filter { it.isPassthroughInput && it.parentId == null }
            val sorted = passthroughList.sortedWith(
                compareBy({ it.type != TvInputInfo.TYPE_HDMI }, { it.id })
            )

            var hdmiCounter = 1
            for (info in sorted) {
                val custom = try { info.loadCustomLabel(this)?.toString() } catch (e: Exception) { null }
                val defaultLabel = try { info.loadLabel(this)?.toString() } catch (e: Exception) { null }

                val label = if (!custom.isNullOrBlank()) {
                    custom
                } else if (!defaultLabel.isNullOrBlank()) {
                    defaultLabel
                } else if (info.type == TvInputInfo.TYPE_HDMI) {
                    "HDMI $hdmiCounter"
                } else if (info.type == TvInputInfo.TYPE_COMPOSITE) {
                    "AV"
                } else {
                    info.id
                }

                if (info.type == TvInputInfo.TYPE_HDMI) {
                    hdmiCounter++
                }

                val uri = TvContract.buildChannelUriForPassthroughInput(info.id).toString()
                val icon = if (info.type == TvInputInfo.TYPE_HDMI) R.drawable.ic_hdmi else R.drawable.ic_inputs
                list.add(InputDef(info.id, label, icon, uri, isAction = false))
            }
        } catch (e: Exception) {
            // In case of reflection/security restrictions on rare OEM builds
        }

        return list
    }

    private fun getSavedInputsOrder(availableIds: List<String>): List<String> {
        val raw = prefs.getString(KEY_INPUTS_ORDER, null)
        if (!raw.isNullOrEmpty()) {
            val saved = raw.split(",").filter { it.isNotEmpty() }
            val valid = saved.filter { availableIds.contains(it) }
            if (valid.isNotEmpty()) {
                val result = valid.toMutableList()
                for (id in availableIds) {
                    if (!result.contains(id)) result.add(id)
                }
                return result
            }
        }
        return availableIds
    }

    private fun saveInputsOrder(orderList: List<String>) {
        prefs.edit().putString(KEY_INPUTS_ORDER, orderList.joinToString(",")).apply()
    }

    private fun getHiddenInputs(): Set<String> {
        val raw = prefs.getString(KEY_HIDDEN_INPUTS, null)
        return if (!raw.isNullOrEmpty()) {
            raw.split(",").filter { it.isNotEmpty() }.toSet()
        } else {
            emptySet()
        }
    }

    private fun saveHiddenInputs(hiddenSet: Set<String>) {
        prefs.edit().putString(KEY_HIDDEN_INPUTS, hiddenSet.joinToString(",")).apply()
    }

    private fun loadInputs() {
        val newInputs = discoverTvInputs()
        if (newInputs.isEmpty()) {
            if (allInputs.isEmpty()) {
                // TV is still booting / initializing hardware inputs, retry in 1.5s
                dpadHandler.postDelayed({ loadInputs() }, 1500)
            }
            return
        }
        allInputs = newInputs
        inputsContainer.removeAllViews()
        val inputMap = allInputs.associateBy { it.id }
        val savedOrder = getSavedInputsOrder(allInputs.map { it.id })

        currentInputsOrder.clear()
        for (id in savedOrder) {
            if (inputMap.containsKey(id)) {
                currentInputsOrder.add(id)
            }
        }
        for (input in allInputs) {
            if (!currentInputsOrder.contains(input.id)) {
                currentInputsOrder.add(input.id)
            }
        }
        saveInputsOrder(currentInputsOrder)

        val hiddenInputs = getHiddenInputs()
        val inflater = LayoutInflater.from(this)

        for (id in currentInputsOrder) {
            if (hiddenInputs.contains(id)) continue
            val input = inputMap[id] ?: continue

            val itemView = inflater.inflate(R.layout.item_input, inputsContainer, false)
            itemView.tag = TAG_TYPE_INPUT + input.id

            val iconView = itemView.findViewById<ImageView>(R.id.input_icon)
            val titleView = itemView.findViewById<TextView>(R.id.input_title)

            iconView.setImageResource(input.iconRes)
            titleView.text = input.title

            itemView.setOnClickListener {
                if (isMoveMode) {
                    if (!waitingForInitialOkRelease) exitMoveMode(true)
                } else if (!handledAsLongPress) {
                    launchInput(input)
                }
            }

            setupCardFocusAnimation(itemView)
            inputsContainer.addView(itemView)
        }
    }

    private fun launchInput(input: InputDef) {
        launchPassthroughUri(input.uriOrAction)
    }

    private fun launchPassthroughUri(uriString: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(uriString)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, getString(R.string.error_launch_source), Toast.LENGTH_SHORT).show()
        }
    }

    private fun showHiddenInputsDialog() {
        val hidden = getHiddenInputs().toMutableSet()
        val names = allInputs.map { it.title }.toTypedArray()
        val checked = BooleanArray(allInputs.size) { i -> !hidden.contains(allInputs[i].id) }

        AlertDialog.Builder(this, AlertDialog.THEME_DEVICE_DEFAULT_DARK)
            .setTitle(getString(R.string.dialog_hidden_inputs_title))
            .setMultiChoiceItems(names, checked) { _, which, isChecked ->
                checked[which] = isChecked
            }
            .setPositiveButton(getString(R.string.btn_save)) { _, _ ->
                val newHidden = mutableSetOf<String>()
                for (i in allInputs.indices) {
                    if (!checked[i]) {
                        newHidden.add(allInputs[i].id)
                    }
                }
                saveHiddenInputs(newHidden)
                loadInputs()
            }
            .setNegativeButton(getString(R.string.btn_cancel), null)
            .show()
    }

    // =========================================================================
    // Apps Loading & Handling
    // =========================================================================

    private fun getSavedAppsOrder(): List<String> {
        val raw = prefs.getString(KEY_APPS_ORDER, null)
        return if (!raw.isNullOrEmpty()) {
            raw.split(",").filter { it.isNotEmpty() }
        } else {
            emptyList()
        }
    }

    private fun saveAppsOrder(orderList: List<String>) {
        prefs.edit().putString(KEY_APPS_ORDER, orderList.joinToString(",")).apply()
    }

    private fun getHiddenApps(): Set<String> {
        val raw = prefs.getString(KEY_HIDDEN_APPS, null)
        return if (!raw.isNullOrEmpty()) {
            raw.split(",").filter { it.isNotEmpty() }.toSet()
        } else {
            emptySet()
        }
    }

    private fun saveHiddenApps(hiddenSet: Set<String>) {
        prefs.edit().putString(KEY_HIDDEN_APPS, hiddenSet.joinToString(",")).apply()
    }

    private fun loadInstalledApps() {
        appsContainer.removeAllViews()
        val pm = packageManager

        val leanbackIntent = Intent(Intent.ACTION_MAIN, null).apply {
            addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER)
        }
        val rawApps = pm.queryIntentActivities(leanbackIntent, 0)

        val systemExcluded = setOf(
            packageName,
            "com.google.android.tvlauncher",
            "com.android.tv.settings",
            "com.spocky.projengmenu",
            "com.mstar.android.tv.disclaimercustomization",
            "com.mediatek.wwtv.webview",
            "mitv.service"
        )

        currentAllInstalledApps.clear()
        val appMap = mutableMapOf<String, ResolveInfo>()
        for (info in rawApps) {
            val pkg = info.activityInfo.packageName
            if (!systemExcluded.contains(pkg)) {
                currentAllInstalledApps.add(info)
                appMap[pkg] = info
            }
        }

        // Apply saved order
        val savedOrder = getSavedAppsOrder()
        currentAppsOrder.clear()
        for (pkg in savedOrder) {
            if (appMap.containsKey(pkg)) {
                currentAppsOrder.add(pkg)
            }
        }
        for (info in currentAllInstalledApps) {
            val pkg = info.activityInfo.packageName
            if (!currentAppsOrder.contains(pkg)) {
                currentAppsOrder.add(pkg)
            }
        }
        saveAppsOrder(currentAppsOrder)

        val hiddenApps = getHiddenApps()
        val visibleApps = currentAppsOrder
            .filter { !hiddenApps.contains(it) && appMap.containsKey(it) }
            .mapNotNull { appMap[it] }

        val inflater = LayoutInflater.from(this)
        for (app in visibleApps) {
            val pkgName = app.activityInfo.packageName
            val itemView = inflater.inflate(R.layout.item_app, appsContainer, false)
            itemView.tag = TAG_TYPE_APP + pkgName

            val bannerView = itemView.findViewById<ImageView>(R.id.app_banner)
            val fallbackContainer = itemView.findViewById<View>(R.id.fallback_container)
            val iconView = itemView.findViewById<ImageView>(R.id.app_icon)
            val titleView = itemView.findViewById<TextView>(R.id.app_title)

            // Try loading 16:9 Leanback banner
            var banner: Drawable? = null
            try {
                banner = app.activityInfo.loadBanner(pm)
                if (banner == null && app.activityInfo.applicationInfo != null) {
                    banner = app.activityInfo.applicationInfo.loadBanner(pm)
                }
                if (banner == null) {
                    banner = app.activityInfo.loadLogo(pm)
                }
                if (banner == null && app.activityInfo.applicationInfo != null) {
                    banner = app.activityInfo.applicationInfo.loadLogo(pm)
                }
            } catch (ignored: Exception) {}

            if (banner != null) {
                bannerView.setImageDrawable(banner)
                bannerView.visibility = View.VISIBLE
                fallbackContainer.visibility = View.GONE
            } else {
                bannerView.visibility = View.GONE
                fallbackContainer.visibility = View.VISIBLE
                iconView.setImageDrawable(app.loadIcon(pm))
                titleView.text = app.loadLabel(pm)
            }

            itemView.setOnClickListener {
                if (isMoveMode) {
                    if (!waitingForInitialOkRelease) exitMoveMode(true)
                } else if (!handledAsLongPress) {
                    launchApp(pkgName)
                }
            }

            setupCardFocusAnimation(itemView)
            appsContainer.addView(itemView)
        }
    }

    private fun launchApp(pkgName: String) {
        val pm = packageManager
        var intent = pm.getLeanbackLaunchIntentForPackage(pkgName)
        if (intent == null) {
            intent = pm.getLaunchIntentForPackage(pkgName)
        }
        if (intent != null) {
            try {
                startActivity(intent)
            } catch (e: Exception) {
                Toast.makeText(this, "Ошибка запуска", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showHiddenAppsDialog() {
        val pm = packageManager
        val hiddenApps = getHiddenApps()
        val sorted = currentAllInstalledApps.sortedBy { it.loadLabel(pm).toString().lowercase() }

        val names = sorted.map { it.loadLabel(pm) }.toTypedArray()
        val checked = BooleanArray(sorted.size) { i -> !hiddenApps.contains(sorted[i].activityInfo.packageName) }

        AlertDialog.Builder(this, AlertDialog.THEME_DEVICE_DEFAULT_DARK)
            .setTitle(getString(R.string.dialog_hidden_apps_title))
            .setMultiChoiceItems(names, checked) { _, which, isChecked ->
                checked[which] = isChecked
            }
            .setPositiveButton(getString(R.string.btn_save)) { _, _ ->
                val newHidden = mutableSetOf<String>()
                for (i in sorted.indices) {
                    if (!checked[i]) {
                        newHidden.add(sorted[i].activityInfo.packageName)
                    }
                }
                saveHiddenApps(newHidden)
                loadInstalledApps()
            }
            .setNegativeButton(getString(R.string.btn_cancel), null)
            .show()
    }

    // =========================================================================
    // Move Mode & Key Navigation (Unified for Apps & Inputs)
    // =========================================================================

    private fun enterMoveMode(targetView: View) {
        isMoveMode = true
        waitingForInitialOkRelease = true
        movingView = targetView
        movingContainer = targetView.parent as? LinearLayout

        // Notice: NO border! Just elevation and enlargement
        movingView?.animate()?.scaleX(1.15f)?.scaleY(1.15f)?.translationZ(16f)?.setDuration(120)?.start()
        Toast.makeText(this, "← → перемещайте стрелками, ОК — зафиксировать", Toast.LENGTH_SHORT).show()
    }

    private fun exitMoveMode(showToast: Boolean) {
        if (isMoveMode) {
            isMoveMode = false
            waitingForInitialOkRelease = false
            isDpadCenterDown = false
            dpadHandler.removeCallbacks(enterMoveModeRunnable)
            dpadHandler.removeCallbacks(openHiddenManagerRunnable)

            movingView?.let { view ->
                val hasFocus = view.hasFocus()
                val targetScale = if (hasFocus) 1.08f else 1.0f
                val targetZ = if (hasFocus) 8f else 0f
                view.animate().scaleX(targetScale).scaleY(targetScale).translationZ(targetZ).setDuration(120).start()
            }
            movingView = null
            movingContainer = null

            if (showToast) {
                Toast.makeText(this, "Порядок сохранен", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun moveCard(direction: Int) {
        val view = movingView ?: return
        val container = movingContainer ?: return

        val currentIndex = container.indexOfChild(view)
        if (currentIndex == -1) return

        val targetIndex = currentIndex + direction
        if (targetIndex < 0 || targetIndex >= container.childCount) {
            return
        }

        container.removeView(view)
        container.addView(view, targetIndex)
        view.requestFocus()

        // Keep 1.15x scale and elevation while moving
        view.scaleX = 1.15f
        view.scaleY = 1.15f
        view.translationZ = 16f

        // Save updated order
        if (container == appsContainer) {
            val newOrder = mutableListOf<String>()
            for (i in 0 until appsContainer.childCount) {
                val tag = appsContainer.getChildAt(i).tag as? String ?: continue
                if (tag.startsWith(TAG_TYPE_APP)) {
                    newOrder.add(tag.removePrefix(TAG_TYPE_APP))
                }
            }
            for (pkg in currentAppsOrder) {
                if (!newOrder.contains(pkg)) newOrder.add(pkg)
            }
            currentAppsOrder = newOrder
            saveAppsOrder(currentAppsOrder)
        } else if (container == inputsContainer) {
            val newOrder = mutableListOf<String>()
            for (i in 0 until inputsContainer.childCount) {
                val tag = inputsContainer.getChildAt(i).tag as? String ?: continue
                if (tag.startsWith(TAG_TYPE_INPUT)) {
                    newOrder.add(tag.removePrefix(TAG_TYPE_INPUT))
                }
            }
            for (id in currentInputsOrder) {
                if (!newOrder.contains(id)) newOrder.add(id)
            }
            currentInputsOrder = newOrder
            saveInputsOrder(currentInputsOrder)
        }
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        val keyCode = event.keyCode
        val action = event.action

        val isDpadOk = (keyCode == KeyEvent.KEYCODE_DPAD_CENTER ||
                        keyCode == KeyEvent.KEYCODE_ENTER ||
                        keyCode == KeyEvent.KEYCODE_NUMPAD_ENTER)

        if (keyCode == KeyEvent.KEYCODE_TV_INPUT) {
            if (action == KeyEvent.ACTION_UP) {
                if (inputsContainer.childCount > 0) {
                    inputsContainer.getChildAt(0).requestFocus()
                }
            }
            return true
        }

        if (isMoveMode) {
            if (action == KeyEvent.ACTION_DOWN) {
                when (keyCode) {
                    KeyEvent.KEYCODE_DPAD_LEFT -> {
                        moveCard(-1)
                        return true
                    }
                    KeyEvent.KEYCODE_DPAD_RIGHT -> {
                        moveCard(1)
                        return true
                    }
                    KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_DPAD_DOWN -> {
                        exitMoveMode(true)
                        return super.dispatchKeyEvent(event)
                    }
                    KeyEvent.KEYCODE_BACK -> {
                        if (event.repeatCount == 0) exitMoveMode(true)
                        return true
                    }
                    else -> {
                        if (isDpadOk) {
                            if (waitingForInitialOkRelease) return true
                            if (event.repeatCount == 0) exitMoveMode(true)
                            return true
                        }
                    }
                }
            } else if (action == KeyEvent.ACTION_UP) {
                if (isDpadOk) {
                    isDpadCenterDown = false
                    dpadHandler.removeCallbacks(enterMoveModeRunnable)
                    dpadHandler.removeCallbacks(openHiddenManagerRunnable)
                    if (waitingForInitialOkRelease) {
                        waitingForInitialOkRelease = false
                        return true
                    }
                    return true
                }
                if (keyCode == KeyEvent.KEYCODE_BACK ||
                    keyCode == KeyEvent.KEYCODE_DPAD_LEFT || keyCode == KeyEvent.KEYCODE_DPAD_RIGHT) {
                    return true
                }
            }
            return true
        }

        // Normal mode (not in move mode)
        val focused = currentFocus
        val tag = focused?.tag as? String ?: ""
        val isCardFocused = tag.startsWith(TAG_TYPE_APP) || tag.startsWith(TAG_TYPE_INPUT)

        if (isCardFocused) {
            if (isDpadOk) {
                if (action == KeyEvent.ACTION_DOWN) {
                    if (event.repeatCount == 0) {
                        isDpadCenterDown = true
                        handledAsLongPress = false
                        dpadTargetView = focused

                        dpadHandler.postDelayed(enterMoveModeRunnable, 500)
                        dpadHandler.postDelayed(openHiddenManagerRunnable, 1600)
                    }
                    return true
                } else if (action == KeyEvent.ACTION_UP) {
                    if (isDpadCenterDown) {
                        isDpadCenterDown = false
                        dpadHandler.removeCallbacks(enterMoveModeRunnable)
                        dpadHandler.removeCallbacks(openHiddenManagerRunnable)

                        if (!handledAsLongPress && dpadTargetView != null) {
                            if (tag.startsWith(TAG_TYPE_APP)) {
                                launchApp(tag.removePrefix(TAG_TYPE_APP))
                            } else if (tag.startsWith(TAG_TYPE_INPUT)) {
                                val inputId = tag.removePrefix(TAG_TYPE_INPUT)
                                val input = allInputs.find { it.id == inputId }
                                if (input != null) launchInput(input)
                            }
                        }
                        dpadTargetView = null
                        return true
                    }
                    return true
                }
            }
        }

        return super.dispatchKeyEvent(event)
    }

    private fun setupCardFocusAnimation(view: View) {
        view.setOnFocusChangeListener { v, hasFocus ->
            if (isMoveMode && v == movingView) return@setOnFocusChangeListener
            if (hasFocus) {
                v.animate().scaleX(1.08f).scaleY(1.08f).translationZ(8f).setDuration(120).start()
            } else {
                v.animate().scaleX(1.0f).scaleY(1.0f).translationZ(0f).setDuration(120).start()
            }
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (isMoveMode) {
            exitMoveMode(true)
        }
    }
}
