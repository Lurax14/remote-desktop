// signaling/__tests__/server.test.js
const { createServer } = require('http')
const { Server } = require('socket.io')
const { io: ioClient } = require('socket.io-client')
const { attachHandlers } = require('../server')

let serverInstance, port

beforeAll((done) => {
  const httpServer = createServer()
  const ioInstance = new Server(httpServer, { cors: { origin: '*' } })

  // Use the real handler logic from server.js — no duplication
  attachHandlers(ioInstance)

  httpServer.listen(() => {
    port = httpServer.address().port
    serverInstance = httpServer
    done()
  })
})

afterAll((done) => {
  serverInstance.close(done)
})

test('segundo cliente recebe peer-ready ao entrar na sala', (done) => {
  const c1 = ioClient(`http://localhost:${port}`)
  const c2 = ioClient(`http://localhost:${port}`)

  // server emits 'peer-ready' to everyone already in the room when a new
  // client joins — so c1 (first joiner) receives it when c2 joins
  c1.on('peer-ready', () => {
    c1.disconnect()
    c2.disconnect()
    done()
  })

  // Wait for c1 to connect and join before c2 joins, to avoid a race condition
  c1.on('connect', () => {
    c1.emit('join', 'sala-teste')
    // Wait for c2 to connect, then join sequentially after c1's join is processed
    c2.on('connect', () => {
      c2.emit('join', 'sala-teste')
    })
  })
}, 10000)

test('offer é retransmitido para o outro cliente', (done) => {
  const c1 = ioClient(`http://localhost:${port}`)
  const c2 = ioClient(`http://localhost:${port}`)

  c2.on('offer', (sdp) => {
    expect(sdp).toBe('fake-sdp')
    c1.disconnect()
    c2.disconnect()
    done()
  })

  // Join both clients sequentially via connect events, then send offer
  c1.on('connect', () => {
    c1.emit('join', 'sala-offer')
    c2.on('connect', () => {
      c2.emit('join', 'sala-offer')
      // c1 sends offer after both are in the room
      c1.emit('offer', { roomId: 'sala-offer', sdp: 'fake-sdp' })
    })
  })
}, 10000)

test('terceiro cliente recebe room-full e não entra na sala', (done) => {
  const c1 = ioClient(`http://localhost:${port}`)
  const c2 = ioClient(`http://localhost:${port}`)
  const c3 = ioClient(`http://localhost:${port}`)

  c3.on('room-full', () => {
    c1.disconnect()
    c2.disconnect()
    c3.disconnect()
    done()
  })

  c1.on('connect', () => {
    c1.emit('join', 'sala-cheia')
    c2.on('connect', () => {
      c2.emit('join', 'sala-cheia')
      c3.on('connect', () => {
        c3.emit('join', 'sala-cheia')
      })
    })
  })
}, 10000)

test('join ignora roomId inválido (não-string)', (done) => {
  const c1 = ioClient(`http://localhost:${port}`)

  // Send an invalid roomId — server should silently ignore it (no crash)
  c1.on('connect', () => {
    c1.emit('join', 12345)
    // If the server didn't crash within 300ms, we're good
    setTimeout(() => {
      c1.disconnect()
      done()
    }, 300)
  })
}, 5000)
