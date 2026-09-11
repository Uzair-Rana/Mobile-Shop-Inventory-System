import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electron', {
  getVersion: () => ipcRenderer.invoke('get-version'),
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
  showDialog: (options) => ipcRenderer.invoke('show-dialog', options),
})

contextBridge.exposeInMainWorld('api', {
  ipcRenderer,
})
