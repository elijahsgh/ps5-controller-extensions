import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasma5support as Plasma5Support

PlasmoidItem {
    id: root

    property var controllers: []
    property string scriptPath: Qt.resolvedUrl("main.qml").toString().replace("file://", "").replace("ui/main.qml", "scripts/ps5_manager.py")

    Plasma5Support.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []

        onNewData: function(sourceName, data) {
            disconnectSource(sourceName)
            if (data["exit code"] === 0) {
                try {
                    let result = JSON.parse(data.stdout)
                    if (Array.isArray(result)) {
                        root.controllers = result
                    }
                } catch(e) {
                    console.error("Failed to parse JSON: " + e)
                }
            }
        }
    }

    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: {
            executable.connectSource("python3 " + root.scriptPath)
        }
    }

    Component.onCompleted: {
        executable.connectSource("python3 " + root.scriptPath)
    }

    compactRepresentation: Item {
        Layout.minimumWidth: root.controllers.length > 0 ? (Kirigami.Units.iconSizes.smallMedium + percentLabel.implicitWidth + Kirigami.Units.smallSpacing * 3) : Kirigami.Units.iconSizes.smallMedium
        Layout.preferredWidth: Layout.minimumWidth

        MouseArea {
            anchors.fill: parent
            onClicked: root.expanded = !root.expanded
        }

        RowLayout {
            anchors.centerIn: parent
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Icon {
                id: iconItem
                Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium
                Layout.preferredHeight: Kirigami.Units.iconSizes.smallMedium
                source: "input-gaming"
            }

            Label {
                id: percentLabel
                visible: root.controllers.length > 0
                text: root.controllers.length > 0 ? root.controllers[0].capacity + "%" : ""
                font.bold: true
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }

    fullRepresentation: Item {
        Layout.minimumWidth: Kirigami.Units.gridUnit * 12
        Layout.minimumHeight: Kirigami.Units.gridUnit * 6

        ColumnLayout {
            anchors.centerIn: parent
            spacing: Kirigami.Units.smallSpacing

            Label {
                visible: root.controllers.length === 0
                text: "No PS5 Controllers Connected"
                Layout.alignment: Qt.AlignHCenter
                font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.2
            }

            Repeater {
                model: root.controllers
                delegate: ColumnLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: Kirigami.Units.smallSpacing

                    Label {
                        text: modelData.name + " Battery:"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: Kirigami.Units.largeSpacing

                        Label {
                            text: modelData.capacity + "%"
                            font.bold: true
                            font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.5
                        }

                        Rectangle {
                            width: Kirigami.Units.gridUnit * 4
                            height: Kirigami.Units.gridUnit * 1.2
                            color: Kirigami.Theme.backgroundColor
                            border.color: Kirigami.Theme.textColor
                            border.width: 1
                            radius: 4

                            Rectangle {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                anchors.margins: 2
                                width: (parent.width - 4) * (Math.max(0, modelData.capacity) / 100.0)
                                color: modelData.capacity <= 15 ? Kirigami.Theme.negativeTextColor : 
                                       (modelData.capacity <= 40 ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.positiveTextColor)
                                radius: 2
                            }
                        }
                    }

                    Button {
                        text: "Turn Off"
                        icon.name: "system-shutdown"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: {
                            executable.connectSource("python3 " + root.scriptPath + " turnoff " + modelData.id)
                            refreshTimer.start()
                        }
                    }
                    
                    Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
                }
            }
        }
    }

    Timer {
        id: refreshTimer
        interval: 2000
        onTriggered: executable.connectSource("python3 " + root.scriptPath)
    }
}
