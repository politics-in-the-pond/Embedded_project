var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var WebSocket = require('ws')
var http = require('http')
var spawn = require('child_process').spawn;

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();

const port = 8088

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.engine('html', require('ejs').renderFile);

app.use(logger('dev'));
app.use(express.static("views"))
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);

// catch 404 and forward to error handlerr
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

var result = spawn('python', ['./hand_recog_temp.py']);
result.stdout.on('data', function(data) {
  console.log(data.toString())
  sockets.forEach((aSocket) => aSocket.send(makeMessage("message", data.toString())));
});

function makeMessage(type, payload) {
  const msg = {type, payload};
  return JSON.stringify(msg)      
}

const handleListening = () => console.log(`Server opened on port ${port}`)

const server = http.createServer(app);
const wss = new WebSocket.Server({server})
const sockets = [];
var msg="aaa"
wss.on("connection",(socket)=>{
  sockets.push(socket)
  console.log("Connected to Browser");
  socket.on("close", ()=>console.log("Disconnected to Browser"));
  socket.on("message", (msg)=>{
      const message = JSON.parse(msg);
      console.log(message)
  });
})

server.listen(port,handleListening)

module.exports = app;
