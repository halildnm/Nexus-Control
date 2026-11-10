import QtQuick
import qs.Common
import qs.Services
import qs.Widgets
import qs.DCommon.Widgets
import qs.Modules.Plugins

PluginComponent {
    id: root

    property string baseUrl: (pluginData.baseUrl || "http://127.0.0.1:8765").replace(/\/$/, "")
    property string token: pluginData.token || ""
    property real cpuLoad: 0
    property real ramLoad: 0
    property bool connected: false
    property string hint: "Nexus"

    function refresh() {
        if (!token || !baseUrl) {
            connected = false
            hint = "Nexus ayarla"
            return
        }
        var xhr = new XMLHttpRequest()
        xhr.open("GET", baseUrl + "/api/status")
        xhr.setRequestHeader("X-Nexus-Token", token)
        xhr.timeout = 1800
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE)
                return
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText)
                    cpuLoad = Number(data.cpu || 0)
                    ramLoad = Number((data.memory || {}).percent || 0)
                    connected = true
                    hint = "Nexus · " + Math.round(cpuLoad) + "% CPU"
                } catch (e) {
                    connected = false
                    hint = "Veri okunamadı"
                }
            } else {
                connected = false
                hint = xhr.status === 401 ? "Token hatalı" : "Bağlantı yok"
            }
        }
        xhr.onerror = function() { connected = false; hint = "Bağlantı yok" }
        xhr.ontimeout = function() { connected = false; hint = "Zaman aşımı" }
        xhr.send()
    }

    Component.onCompleted: refresh()
    Timer { interval: 3000; running: true; repeat: true; onTriggered: root.refresh() }

    horizontalBarPill: Component {
        Row {
            spacing: Theme.spacingS
            DIcon {
                name: "devices"
                size: Theme.iconSize
                color: root.connected ? Theme.primary : Theme.surfaceVariantText
                anchors.verticalCenter: parent.verticalCenter
            }
            StyledText {
                text: root.connected ? ("NEXUS  " + Math.round(root.cpuLoad) + "%")
                                     : "NEXUS  ·"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.surfaceText
                anchors.verticalCenter: parent.verticalCenter
            }
            MouseArea {
                anchors.fill: parent
                onClicked: Qt.openUrlExternally(root.baseUrl)
                cursorShape: Qt.PointingHandCursor
            }
        }
    }

    verticalBarPill: Component {
        Column {
            spacing: Theme.spacingXS
            DIcon {
                name: "devices"
                size: Theme.iconSize
                color: root.connected ? Theme.primary : Theme.surfaceVariantText
                anchors.horizontalCenter: parent.horizontalCenter
            }
            StyledText {
                text: root.connected ? Math.round(root.cpuLoad) + "%" : "NEXUS"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.surfaceText
                anchors.horizontalCenter: parent.horizontalCenter
            }
            MouseArea {
                anchors.fill: parent
                onClicked: Qt.openUrlExternally(root.baseUrl)
                cursorShape: Qt.PointingHandCursor
            }
        }
    }
}
