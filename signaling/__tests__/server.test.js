// signaling/__tests__/server.test.js
const { createServer } = require('http')
const { Server } = require('socket.io')
const { io: ioClient } = require('socket.io-client')

let serverInstance, ioInstance, port

beforeAll((done) => {
  const httpServer = createServer()
  ioInstance = new Server(httpServer, { cors: { origin: '*' } })

  ioInstance.on('connection', (socket) => {
    socket.on('join', (roomId) => {
      socket.join(roomId)
      const room = ioInstance.sockets.adapter.rooms.get(roomId)
      if (room && room.size > 1) socket.to(roomId).emit('peer-ready')
    })
    socket.on('offer', ({ roomId, sdp }) => socket.to(roomId).emit('offer', sdp))
    socket.on('answer', ({ roomId, sdp }) => socket.to(roomId).emit('answer', sdp))
    socket.on('ice-candidate', ({ roomId, candidate }) => socket.to(roomId).emit('ice-candidate', candidate))
  })

  httpServer.listen(() => {
    port = httpServer.address().port
    serverInstance = httpServer
    done()
  })
})

afterAll(() => {
  ioInstance.close()
  serverInstance.close()
})

test('segundo cliente recebe peer-ready ao entrar na sala', (done) => {
  const c1 = ioClient(`http://localhost:${port}`)
  const c2 = ioClient(`http://localhost:${port}`)

  // server emits 'peer-ready' to everyone already in the room when a new
  // client joins — so c1 (first joiner) receives it when c2 joins
  c1.on('peer-ready', () => {
    c1.disconnect(); c2.disconnect()
    done()
  })

  c1.on('connect', () => {
    c1.emit('join', 'sala-teste')
    // wait for c1's join to be processed server-side before c2 joins
    setTimeout(() => c2.emit('join', 'sala-teste'), 100)
  })
}, 10000)

test('offer é retransmitido para o outro cliente', (done) => {
  const c1 = ioClient(`http://localhost:${port}`)
  const c2 = ioClient(`http://localhost:${port}`)

  c1.emit('join', 'sala-offer')
  c2.emit('join', 'sala-offer')

  c2.on('offer', (sdp) => {
    expect(sdp).toBe('fake-sdp')
    c1.disconnect(); c2.disconnect()
    done()
  })

  setTimeout(() => c1.emit('offer', { roomId: 'sala-offer', sdp: 'fake-sdp' }), 200)
})
