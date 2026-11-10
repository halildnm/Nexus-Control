import QtQuick
import qs.Common
import qs.Modules.Plugins
import qs.Widgets

PluginSettings {
    id: root
    pluginId: "nexusControl"

    StyledText {
        width: parent.width
        text: "Nexus Control bağlantısı"
        font.pixelSize: Theme.fontSizeLarge
        font.weight: Font.Bold
        color: Theme.surfaceText
    }

    StyledText {
        width: parent.width
        text: "Nexus masaüstü uygulamasını başlatın. iPad erişimi için kullandığınız bilgisayarın LAN adresini girin."
        font.pixelSize: Theme.fontSizeSmall
        color: Theme.surfaceVariantText
        wrapMode: Text.WordWrap
    }

    StringSetting {
        settingKey: "baseUrl"
        label: "Nexus adresi"
        description: "Örnek: http://192.168.1.20:8765"
        placeholder: "http://127.0.0.1:8765"
        defaultValue: "http://127.0.0.1:8765"
    }

    StringSetting {
        settingKey: "token"
        label: "Erişim anahtarı"
        description: "Nexus masaüstü uygulamasındaki erişim anahtarı"
        placeholder: "NEXUS token"
        defaultValue: ""
    }
}
