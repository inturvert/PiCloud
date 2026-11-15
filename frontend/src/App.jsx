
import { useEffect, useState } from 'react'
import {
  Cloud,
  File,
  FileText,
  Image,
  Video,
  Music,
  RefreshCw,
  Download,
  HardDrive,
  AlertCircle,
} from 'lucide-react'

import { getFiles, scanStorage } from './api'

function formatSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const index = Math.floor(Math.log(bytes) / Math.log(1024))

  return `${(bytes / Math.pow(1024, index)).toFixed(2)} ${units[index]}`
}

function getFileIcon(mimeType) {
  if (!mimeType) return File

  if (mimeType.startsWith('image/')) return Image
  if (mimeType.startsWith('video/')) return Video
  if (mimeType.startsWith('audio/')) return Music
  if (mimeType === 'application/pdf') return FileText

  return File
}

export default function App() {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function loadFiles() {
    try {
      setError('')

      const data = await getFiles()
      setFiles(data.files)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function refreshStorage() {
    try {
      setScanning(true)
      setError('')
      setMessage('')

      const result = await scanStorage()

      await loadFiles()

      setMessage(
        `Scan completed. ${result.discovered} new file(s) discovered.`
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setScanning(false)
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  const totalSize = files.reduce(
    (total, file) => total + file.size,
    0
  )

  return (
    <div className="min-h-screen bg-slate-50">

      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">

          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-xl text-white">
              <Cloud size={25} />
            </div>

            <div>
              <h1 className="text-xl font-bold text-slate-900">
                PiCloud
              </h1>

              <p className="text-xs text-slate-500">
                Your personal cloud storage
              </p>
            </div>
          </div>

          <button
            onClick={refreshStorage}
            disabled={scanning}
            className="flex items-center gap-2 bg-blue-600
              hover:bg-blue-700 disabled:opacity-50
              text-white px-4 py-2 rounded-lg text-sm"
          >
            <RefreshCw
              size={16}
              className={scanning ? 'animate-spin' : ''}
            />

            {scanning ? 'Scanning...' : 'Refresh storage'}
          </button>

        </div>
      </header>

      {/* Main */}
      <main className="max-w-6xl mx-auto px-6 py-10">

        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900">
            My Files
          </h2>

          <p className="text-slate-500 mt-1">
            Files stored on your PiCloud server.
          </p>
        </div>

        {/* Storage summary */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">

          <div className="bg-white border border-slate-200
            rounded-xl p-5 flex items-center gap-4">

            <div className="bg-blue-50 text-blue-600 p-3 rounded-lg">
              <HardDrive size={24} />
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Registered files
              </p>

              <p className="text-xl font-bold">
                {files.length}
              </p>
            </div>
          </div>

          <div className="bg-white border border-slate-200
            rounded-xl p-5 flex items-center gap-4">

            <div className="bg-indigo-50 text-indigo-600 p-3 rounded-lg">
              <Cloud size={24} />
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Total file size
              </p>

              <p className="text-xl font-bold">
                {formatSize(totalSize)}
              </p>
            </div>
          </div>

        </div>

        {/* Notifications */}
        {message && (
          <div className="mb-5 p-3 rounded-lg bg-green-50
            text-green-700 text-sm">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-5 p-3 rounded-lg bg-red-50
            text-red-700 text-sm flex items-center gap-2">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {/* File list */}
        <div className="bg-white border border-slate-200
          rounded-xl overflow-hidden">

          <div className="px-5 py-4 border-b border-slate-200">
            <h3 className="font-semibold">
              Available files
            </h3>
          </div>

          {loading ? (

            <div className="p-10 text-center text-slate-500">
              Loading files...
            </div>

          ) : files.length === 0 ? (

            <div className="p-12 text-center">
              <Cloud size={42} className="mx-auto text-slate-300" />

              <p className="mt-4 font-medium text-slate-700">
                No files found
              </p>

              <p className="text-sm text-slate-500 mt-1">
                Copy files into your server's storage directory
                and click Refresh storage.
              </p>
            </div>

          ) : (

            <div className="divide-y divide-slate-100">

              {files.map((file) => {

                const Icon = getFileIcon(file.mime_type)

                return (
                  <div
                    key={file.id}
                    className="px-5 py-4 flex items-center
                      justify-between gap-4 hover:bg-slate-50"
                  >

                    <div className="flex items-center gap-4 min-w-0">

                      <div className="bg-blue-50 text-blue-600
                        p-3 rounded-lg shrink-0">
                        <Icon size={22} />
                      </div>

                      <div className="min-w-0">
                        <p className="font-medium text-slate-800
                          truncate">
                          {file.name}
                        </p>

                        <p className="text-xs text-slate-500 mt-1">
                          {formatSize(file.size)}
                          {' · '}
                          {new Date(file.created_at).toLocaleDateString()}
                        </p>
                      </div>

                    </div>

                    <a
                      href={`/api/files/${file.id}/download`}
                      className="flex items-center gap-2
                        text-blue-600 hover:text-blue-800
                        text-sm shrink-0"
                      title="Download file"
                    >
                      <Download size={18} />
                      <span className="hidden sm:inline">
                        Download
                      </span>
                    </a>

                  </div>
                )
              })}

            </div>

          )}

        </div>

      </main>

    </div>
  )
}
