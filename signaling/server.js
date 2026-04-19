// signaling/server.js
const http = require('http')
const { Server } = require('socket.io')

const server = http.createServer()
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
})

/**
 * Attaches all Socket.IO event handlers to the given `io` instance.
 * Extracted so tests can mount the same logic on a fresh in-process server
 * without duplicating handler code.
 */
function attachHandlers (io) {
  io.on('connection', (socket) => {
    socket.on('join', (roomId) => {
      // Input validation
      if (typeof roomId !== 'string' || roomId.length === 0) return

      // Room size cap — only 2 peers allowed (one offerer, one answerer)
      const existingRoom = io.sockets.adapter.rooms.get(roomId)
      if (existingRoom && existingRoom.size >= 2) {
        socket.emit('room-full')
        return
      }

      socket.join(roomId)
      const room = io.sockets.adapter.rooms.get(roomId)

      // 'peer-ready' is sent to the first client (already in the room) because
      // it is the WebRTC initiator: it must create the offer and send it to the
      // newly arrived peer. The newcomer (socket) just joined and waits for
      // the offer, so we do NOT emit to the newcomer here.
      if (room && room.size > 1) {
        socket.to(roomId).emit('peer-ready')
      }
    })

    socket.on('offer', ({ roomId, sdp } = {}) => {
      if (typeof roomId !== 'string') return
      socket.to(roomId).emit('offer', sdp)
    })

    socket.on('answer', ({ roomId, sdp } = {}) => {
      if (typeof roomId !== 'string') return
      socket.to(roomId).emit('answer', sdp)
    })

    socket.on('ice-candidate', ({ roomId, candidate } = {}) => {
      if (typeof roomId !== 'string') return
      socket.to(roomId).emit('ice-candidate', candidate)
    })
  })
}

attachHandlers(io)

const PORT = process.env.PORT || 3000
server.listen(PORT, () => console.log(`Signaling on :${PORT}`))

module.exports = { server, io, attachHandlers }
