const electron = require('electron')
const { app, BrowserWindow } = require('electron')

let loadingScreen;
// Creates the loading window of the application
const createLoadingScreen = () => {
    // Create a browser window
    loadingScreen = new BrowserWindow(
        Object.assign({
            // width and height of the window
            width: 800,
            height: 600,
            // Make windows frameless
            frame: false,
            // Transparency to remove windows background
            transparent: true
        })
    );
    loadingScreen.setResizable(false);
    loadingScreen.loadURL(
        'file://${__dirname}/loading/loading.html'
    );
    loadingScreen.on('closed', () => (loadingScreen = null));
    loadingScreen.webContents.on('did-finish-load', () => {
        loadingScreen.show();
    });
};

// Creates the main window of the application
function createWindow() {
    // Create a browser window.
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        },
        show: false
    })

    // and load the index.html of the app.
    win.loadFile('index.html')
    win.maximize();

    // Keep waiting for the main windows to load
    win.webContents.on('did-finish-load', () => {
        // Once it loads, close loading screen and show main window
        if (loadingScreen) {
            loadingScreen.close();
        }
        win.show();
    })
}

// This method will be called when Electron has finished intialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.

app.on('ready', () => {
    createLoadingScreen();
    // Delay for testing reasons
    setTimeout(() => {
        createWindow();
    }, 1000);
})

// Quit when all windows are closed.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin'){
        app.quit()
    }
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0){
        createWindow()
    }
})
