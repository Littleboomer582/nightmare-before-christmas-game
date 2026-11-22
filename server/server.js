// Dead End Depot game server: a small MQTT broker over WebSocket for online co-op.
// The game already speaks MQTT, so this is a private copy of the public servers it uses,
// made for hosts like Render: one port (PORT), plain HTTP inside, TLS added by the host.
//
//   wss://<your-server>/mqtt   the game connects here
//   https://<your-server>/     a health page: {"ok":true,...} (Render's health check, and the
//                              game's wake-up call when a free server has gone to sleep)
//
// Only this game's topics are relayed, nothing is stored, and sizes and counts are capped.
import { createServer } from 'node:http'
import { Aedes } from 'aedes'
import { WebSocketServer, createWebSocketStream } from 'ws'

const PORT = Number(process.env.PORT) || 10000
const TOPIC = 'deadenddepot/'                                   // the game's topics all start with this
const MAX_CLIENTS = Number(process.env.MAX_CLIENTS) || 200      // four per game: plenty for friends
const MAX_MESSAGE = 256 * 1024                                  // the biggest game message is far smaller
const started = Date.now()

const broker = await Aedes.createBroker({ maxTopicLevels: 8, connectTimeout: 15000, drainTimeout: 15000 })
broker.preConnect = (client, packet, done) => done(null, broker.connectedClients < MAX_CLIENTS)
broker.authorizePublish = (client, packet, done) => {
  if (!packet.topic.startsWith(TOPIC)) return done(new Error('not a game topic'))
  packet.retain = false                                         // keep nothing between games
  done(null)
}
broker.authorizeSubscribe = (client, sub, done) => done(null, sub.topic.startsWith(TOPIC) ? sub : null)

const http = createServer((req, res) => {
  const path = (req.url || '/').split('?')[0]
  if (req.method === 'OPTIONS') { res.writeHead(204, cors()); return res.end() }
  if (path === '/' || path === '/health') {
    res.writeHead(200, { ...cors(), 'Content-Type': 'application/json', 'Cache-Control': 'no-store' })
    return res.end(JSON.stringify({ ok: true, game: 'deadenddepot', players: broker.connectedClients, upMinutes: Math.round((Date.now() - started) / 60000) }))
  }
  res.writeHead(404, { ...cors(), 'Content-Type': 'text/plain' })
  res.end('Dead End Depot game server. The game connects to /mqtt.')
})
function cors () { return { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, OPTIONS' } }

const wss = new WebSocketServer({
  server: http,
  path: '/mqtt',
  maxPayload: MAX_MESSAGE,
  handleProtocols: protocols => (protocols.has('mqtt') ? 'mqtt' : protocols.has('mqttv3.1') ? 'mqttv3.1' : false)
})
wss.on('connection', (socket, req) => {
  const stream = createWebSocketStream(socket)
  stream.on('error', () => socket.terminate())
  broker.handle(stream, req)
})
broker.on('clientError', () => {})                              // a bad client just gets dropped
broker.on('connectionError', () => {})

http.listen(PORT, () => console.log(`Dead End Depot game server on port ${PORT}`))
const stop = () => { wss.close(); http.close(); broker.close(() => process.exit(0)); setTimeout(() => process.exit(0), 3000).unref() }
process.on('SIGTERM', stop)
process.on('SIGINT', stop)
