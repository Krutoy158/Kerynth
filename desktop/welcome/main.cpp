#include <QApplication>
#include <QCheckBox>
#include <QCloseEvent>
#include <QFile>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QProcess>
#include <QPushButton>
#include <QTextBrowser>
#include <QVBoxLayout>
#include <QWidget>
#include <QStandardPaths>

class WelcomeWindow final : public QWidget {
public:
    WelcomeWindow() {
        setWindowTitle("Welcome to Kerynth");
        setMinimumSize(760, 520);
        resize(900, 600);

        mode = readMode();
        auto *root = new QVBoxLayout(this);
        auto *heading = new QLabel("Welcome to Kerynth");
        heading->setStyleSheet("font-size: 26px; font-weight: 600;");
        auto *intro = new QLabel(
            mode == "live"
                ? "You are trying Kerynth in a temporary Live session. Changes may disappear when you shut down."
                : "Your system is ready. This short guide will help you find the essentials."
        );
        intro->setWordWrap(true);

        auto *content = new QHBoxLayout;
        auto *navigation = new QVBoxLayout;
        auto *page = new QTextBrowser;
        page->setOpenExternalLinks(false);

        const QList<QPair<QString, QString>> sections = {
            {"Welcome", "welcome"},
            {"Connect to the Internet", "connect"},
            {"Updates", "updates"},
            {"Drivers and Hardware", "drivers"},
            {"Appearance", "appearance"},
            {"Applications", "apps"},
            {"Backups and Recovery", "backups"},
            {"Help", "help"}
        };

        for (const auto &section : sections) {
            auto *button = new QPushButton(section.first);
            button->setMinimumHeight(38);
            navigation->addWidget(button);
            connect(button, &QPushButton::clicked, this, [this, page, section]() {
                showSection(page, section.second);
            });
        }
        navigation->addStretch();

        content->addLayout(navigation, 1);
        content->addWidget(page, 3);

        auto *footer = new QHBoxLayout;
        showAtStartup = new QCheckBox("Show this guide at startup");
        showAtStartup->setChecked(readPreference());
        auto *done = new QPushButton("Done");
        done->setDefault(true);
        footer->addWidget(showAtStartup);
        footer->addStretch();
        footer->addWidget(done);

        root->addWidget(heading);
        root->addWidget(intro);
        root->addSpacing(8);
        root->addLayout(content, 1);
        root->addLayout(footer);

        connect(done, &QPushButton::clicked, this, &QWidget::close);
        showSection(page, "welcome");
    }

protected:
    void closeEvent(QCloseEvent *event) override {
        savePreference(showAtStartup->isChecked());
        QWidget::closeEvent(event);
    }

private:
    QString mode;
    QCheckBox *showAtStartup = nullptr;

    QString readMode() const {
        QFile file("/run/kerynth/boot-mode");
        if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
            const QString value = QString::fromUtf8(file.readLine()).trimmed();
            if (value == "live" || value == "installed")
                return value;
        }
        return "installed";
    }

    QString stateTool() const {
        return QStandardPaths::findExecutable("kerynth-welcome-state");
    }

    bool readPreference() const {
        const QString tool = stateTool();
        if (tool.isEmpty())
            return true;
        QProcess process;
        process.start(tool, {"should-show", "--mode", mode});
        if (!process.waitForFinished(3000) || process.exitStatus() != QProcess::NormalExit || process.exitCode() != 0)
            return true;
        return QString::fromUtf8(process.readAllStandardOutput()).trimmed() != "hidden";
    }

    void savePreference(bool enabled) const {
        const QString tool = stateTool();
        if (tool.isEmpty())
            return;
        QProcess::startDetached(
            tool,
            {"set", "--mode", mode, enabled ? "--show" : "--hide"}
        );
    }

    bool launchFirstAvailable(const QStringList &candidates) {
        for (const QString &candidate : candidates) {
            const QString executable = QStandardPaths::findExecutable(candidate);
            if (!executable.isEmpty())
                return QProcess::startDetached(executable, {});
        }
        return false;
    }

    void showSection(QTextBrowser *page, const QString &section) {
        QString html;
        QStringList actions;
        QString actionLabel;

        if (section == "welcome") {
            html = "<h2>Your first steps</h2><p>Kerynth is designed to keep everyday work simple and system administration explicit.</p><p>Choose a topic on the left. Every step is optional. You can close this guide now and reopen it later from the Applications menu.</p>";
        } else if (section == "connect") {
            html = "<h2>Connect</h2><p>Open Network settings to connect to Wi-Fi or configure a wired connection. Kerynth will not connect to a network until you choose one.</p>";
            actions = {"systemsettings"};
            actionLabel = "Open System Settings";
        } else if (section == "updates") {
            html = "<h2>Updates</h2><p>Check for system and security updates when an update tool is available. Nothing is downloaded or installed by this guide.</p>";
            actions = {"plasma-discover", "discover"};
            actionLabel = "Open Software Center";
        } else if (section == "drivers") {
            html = "<h2>Drivers and Hardware</h2><p>Use the available system tools to inspect devices and driver status. Hardware information stays on this computer.</p><p>Automatic driver installation is not enabled by this guide.</p>";
            actions = {"systemsettings"};
            actionLabel = "Open System Settings";
        } else if (section == "appearance") {
            html = "<h2>Appearance</h2><p>Personalize the desktop, wallpaper, display scale, and accessibility options using the desktop settings.</p>";
            actions = {"systemsettings"};
            actionLabel = "Open Appearance Settings";
        } else if (section == "apps") {
            html = "<h2>Applications</h2><p>Use the software center to browse available applications. Review each application before installing it.</p>";
            actions = {"plasma-discover", "discover"};
            actionLabel = "Open Software Center";
        } else if (section == "backups") {
            html = "<h2>Backups and Recovery</h2><p>Backup and recovery tools will be listed here when they are included in your Kerynth installation. This feature is not available in the current prototype.</p>";
        } else if (section == "help") {
            html = "<h2>Help</h2><p>Read the documentation included with your system or visit the project documentation after choosing to open it.</p>";
            actions = {"xdg-open"};
            actionLabel = "Open Online Documentation";
        }

        page->setHtml(html);
        if (!actions.isEmpty()) {
            auto *button = new QPushButton(actionLabel);
            page->setCornerWidget(button);
            connect(button, &QPushButton::clicked, this, [this, actions, section]() {
                if (section == "help") {
                    if (!QProcess::startDetached("xdg-open", {"https://github.com/Krutoy158/Kerynth"}))
                        QMessageBox::information(this, "Not available yet", "No desktop web browser is available.");
                    return;
                }
                if (!launchFirstAvailable(actions)) {
                    QMessageBox::information(this, "Not available yet",
                        "The required settings or software application is not installed in this Kerynth build.");
                }
            });
        } else {
            page->setCornerWidget(nullptr);
        }
    }
};

int main(int argc, char *argv[]) {
    QApplication application(argc, argv);
    WelcomeWindow window;
    window.show();
    return application.exec();
}
