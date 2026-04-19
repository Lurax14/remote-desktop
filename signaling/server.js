// signaling/server.js
const http = require('http')
const { Server } = require('socket.io')

const server = http.createServer()
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
})

io.on('connection', (socket) => {
  socket.on('join', (roomId) => {
    socket.join(roomId)
    const room = io.sockets.adapter.rooms.get(roomId)
    if (room && room.size > 1) {
      socket.to(roomId).emit('peer-ready')
    }
  })

  socket.on('offer', ({ roomId, sdp }) => {
    socket.to(roomId).emit('offer', sdp)
  })

  socket.on('answer', ({ roomId, sdp }) => {
    socket.to(roomId).emit('answer', sdp)
  })

  socket.on('ice-candidate', ({ roomId, candidate }) => {
    socket.to(roomId).emit('ice-candidate', candidate)
  })
})

const PORT = process.env.PORT || 3000
server.listen(PORT, () => console.log(`Signaling on :${PORT}`))

module.exports = { server, io }
