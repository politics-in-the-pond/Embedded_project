const WIDTH=1000, HEIGHT=750;
const TILESIZE = 48;
const ROWS = HEIGHT / TILESIZE;
const COLS = WIDTH / TILESIZE;
const MAX_LEVEL = 6;
//S:STOP, L:LEFT, R:RIGHT
var DIRECTION = "S";
var JUMP = false;

var config = {
	type: Phaser.AUTO,
	width: WIDTH,
	height: HEIGHT,
	physics: {
		default: 'arcade',
		arcade: {
			gravity : {y:300},
			debug: false
		}
	},
	scene: {
		preload: preload,
		create: create,
		update:update
	}
}

function makeMessage(type, payload) {
	const msg = {type, payload};
	return JSON.stringify(msg)      
}

function msgParser(msg){
	const MESSAGE = JSON.parse(msg.data).payload;
	console.log(DIRECTION);
	if(MESSAGE == "S" || MESSAGE == "L" || MESSAGE == "R"){
		DIRECTION = MESSAGE;
	}else if(MESSAGE == "J"){
		JUMP = true;
	}else{

	}
}

//웹소켓 연결
socket = new WebSocket(`ws://${window.location.host}`)
socket.addEventListener("message", (message)=>msgParser(message));

var game = new Phaser.Game(config);
//처음 레벨 설정 
var level = -1;  //intro때문에 -1이 시작
var gameover = false;
let diamond_cnt = 0;
let scoreText ='';

function preload() {

	// assets 들 변수 지어주기 
	// intro
	this.load.image('intro1', 'assets/intro1.png');
	this.load.image('intro2', 'assets/intro2.png');
	// stage
	this.load.image('stage1', 'assets/stage_subwaygate.png');
	this.load.image('stage2', 'assets/stage_visiontower.png');
	this.load.image('stage3', 'assets/stage_gachonbuilding.png');
	this.load.image('stage4', 'assets/stage_windwheel.png');
	// outro
	this.load.image('outro1', 'assets/outro1.png');

	this.load.image('sun', 'assets/sun.png');
	this.load.image('fire1', 'tiles/15.png');
	this.load.image('fire2', 'tiles/16.png');
	this.load.image('water1', 'tiles/19.png');
	this.load.image('water2', 'tiles/20.png');
	this.load.image('tree', 'tiles/21.png');
	this.load.image('mushroom', 'tiles/22.png');
	this.load.image('bee', 'tiles/23.png');
	this.load.image('exit', 'tiles/24.png');
	this.load.image('movingp', 'assets/moving.png');
	this.load.image('flower', 'tiles/27.png');
	this.load.image('slime', 'tiles/29.png');

	this.load.spritesheet('student','assets/sizeup_student.png',{
		frameWidth: 72, frameHeight: 45
	})
	// tile들 불러오기 
	for (let i=0; i<13; i++) {
		// loading platforms
		this.load.image(`tile${i+1}`, `tiles/${i+1}.png`);
	}

	for (let i=0; i<4; i++) {
		// loading diamonds
		this.load.image(`d${i+1}`, `assets/d${i+1}.png`);
	}

	this.load.json('levels', 'levels/level.json')
}

function create() {

	
	// intro
	if(level == -1){ //intro1
		this.add.image(0, 0, 'intro1').setOrigin(0).setScrollFactor(0);
		setTimeout(() => {
			level+=1;
			this.scene.restart();
		}, 4000);
	}
	else if(level == 0){ //intro2
		this.add.image(0, 0, 'intro2').setOrigin(0).setScrollFactor(0); 
		setTimeout(() => {
			level+=1;
			this.scene.restart();
		}, 4000);
	}

	// draw background
	else if(level == 1)
		this.add.image(0, 0, 'stage1').setOrigin(0).setScrollFactor(0);
	else if(level == 2)
		this.add.image(0, 0, 'stage2').setOrigin(0).setScrollFactor(0);
	else if(level == 3)
		this.add.image(0, 0, 'stage3').setOrigin(0).setScrollFactor(0);
	else if(level == 4)
		this.add.image(0, 0, 'stage4').setOrigin(0).setScrollFactor(0);
	//outro
	else if(level == 5){
		this.add.image(0, 0, 'outro1').setOrigin(0).setScrollFactor(0);
	}

	scoreText = this.add.text(15, 15, " ", {
		fontSize: "32px",
		fill: "#000",
	});
	 
	//this.add.image(100, 120, 'sun');

	// draw grid
	// drawGrid(this);

	// keypress Events
	cursor = this.input.keyboard.createCursorKeys();

	// create groups
	// 정적그룹으로 설정 
	platforms = this.physics.add.staticGroup();
	diamonds = this.physics.add.staticGroup();
	firewater = this.physics.add.staticGroup();
	greens = this.physics.add.staticGroup();
	exits = this.physics.add.staticGroup();
	//버섯 기능추가 
	mushrooms=this.physics.add.staticGroup();
	bees = this.physics.add.group({allowGravity:false});
	slimes = this.physics.add.group({allowGravity:false});
	movingPlatforms = this.physics.add.group({allowGravity:false, immovable:true});
	
	// loading levels json 
	// 여기서 json 에 저장해놓은거 가져옴 
	var levels = this.cache.json.get('levels');
	loadLevelSetup(levels, level, this);

	

	// creating player
	if(level < 1)
		player = new Player({scene:this, x: 0, y:750});
	else
		player = new Player({scene:this, x: 100, y:300});

	// Collision Detection
	this.physics.add.collider(player, platforms);
	//water collision 의 경우  gameover 
	this.physics.add.collider(player, firewater, gameOver, null, this);
	//bees collision의 경우 gameover 
	this.physics.add.collider(player, bees, gameOver, null, this);
	//slimes collision의 경우 gameover 
	this.physics.add.collider(player, slimes, gameOver, null, this);
	//collisionMovingPlatform collision시 이동
	this.physics.add.collider(player, movingPlatforms, collisionMovingPlatform, null, this);
	//다이아몬드 overlap 경우 collectDiamonds 수행 
	//overlap 과 collestion는 둘다 충돌해서 이벤트 발생하지만 
	//overlap은 만남을 감지하고 어떤 작업을 수행 하는것이다 
	this.physics.add.overlap(player, diamonds, collectDiamonds, null, this);
	//버섯 닿으면 높게 올라가기
	this.physics.add.overlap(player,mushrooms,mushroomUp,null,this);

	// exits 문 접촉했을때 gamewon 
	this.physics.add.collider(player, exits, gameWon, null, this);

	// Text Objects
	//if(level>=1 && level<5)
	//levelText = this.add.text(WIDTH-200, 10, `Stage : ${level}`, {fontSize:'32px', fill:'#000'})

	// draw border
	var rect = this.add.rectangle(0, 0, WIDTH, HEIGHT).setOrigin(0);
	rect.setStrokeStyle(4, 0x1a65ac)

	//set score 
	
	//다이아몬드 모으기 
	
	
}
//캐릭터 움직임 
function update() {
	if (!gameover) {
		//왼쪽 방향키
		if (DIRECTION == "L") {
			player.body.setVelocityX(-100);
			player.anims.play('left', true);
		} //오른쪽 방향기 
		else if (DIRECTION == "R") {
			player.body.setVelocityX(100);
			player.anims.play('right', true);
		}// 가만히 있기 
		else {
			player.body.setVelocityX(0);
			player.anims.play('turn', true);
		}
		// 점프 
		if (JUMP && player.body.touching.down) {
			player.body.setVelocityY(-400);
			JUMP = false;
		}
		 
	}
	
	
	
}
// 레벨마다 맵 다르게 설정하는것 
// 이 부분 코드 이해하면 맵 위치 설정 가능 
//여기서 tiles 의 위치 설정 
function loadLevelSetup(levels, level, scene) {

	level_data = levels[level];
	for (let i=0; i<level_data.length; i++) {
		for (let j=0; j<level_data[0].length; j++) {
			data = level_data[i][j];
			[x, y] = getPos(i, j);

			if (data && data <= 13) {
				platforms.create(x, y,`tile${data}`).setScale(0.4).refreshBody();
			}
			//data =17 은 다이아몬드 
			if (data && data == 17) {
				diamonds.create(x, y,`d${randint(1, 4)}`).setScale(0.4).refreshBody();
			}
			//data =15 or data=16은 불 
			if (data == 15 || data == 16) {
				offy = data == 15 ? 10 : 0;
				[x, y] = getPos(i, j, 0, offy);
				firewater.create(x, y,`fire${data-14}`).setScale(0.4).refreshBody();
			}
			//data =19 or data=20은 물 
			if (data == 19 || data == 20) {
				offy = data == 19 ? 10 : 0;
				[x, y] = getPos(i, j, 0, offy);
				firewater.create(x, y,`water${data-18}`).setScale(0.4).refreshBody();
			}
			// data =21은 나무 
			if (data == 21) {
				greens.create(x, y-34, 'tree');
			}
			// data==2는 버섯
			if (data == 22) {
				greens.create(x, y+12, 'mushroom').refreshBody();
			}
			// data=23 벌
			if (data == 23) {
				var bee = new Bee({scene:scene, x: x, y:y})
				bee.setScale(0.5);
				bees.add(bee);
			}
			// data=24 탈출구 
			if (data == 24) {
				exits.create(x, y, 'exit');
			}
			// 25 는 왼쪽 오른쫌 움직임 ,26은 위아래 
			if (data == 25 || data == 26) {
				type = data == 25 ? 'side' : 'up';
				var movingp = new MovingPlatform({scene:scene, x:x, y:y, key:'movingp', type:type})
				movingPlatforms.add(movingp);
			}

			if (data == 27) {
				var flower = greens.create(x, y+14, 'flower');
				flower.setScale(0.2);
			}

			if (data == 29) {
				var slime = new Slime({scene:scene, x: x, y:y+15, distance:50});
				slime.setScale(0.5);
				slimes.add(slime);
			}
		}
	}
}
// 타일 position 잡는 함수 
//TILESIZE =48 
function getPos(i, j, offsetx=0, offsety=0) {
	return [TILESIZE*(j+1)-24+offsetx, TILESIZE*(i+1)-24+offsety];
}

//게임 끝내기 
function gameOver(player, tile) {
	player.setTint(0xff0000);
	this.physics.pause();
	this.scene.restart();
}
// 레벨 올려주기 
function gameWon(player, tile) {
	if (level < MAX_LEVEL) {
		level += 1;
		console.log(level);
		this.scene.restart();
	}
	if(level == MAX_LEVEL){
		setTimeout(() => {
			location.reload(true); //포탈가면 새로고침해서 게임 다시 시작
		}, 1000);
	}
}
//움직이는 발판 
function collisionMovingPlatform(player, platform) {
	if (platform.body.touching.up && player.body.touching.down){
		if (platform.body.y > player.body.y) {
		    player.body.x += platform.vx;
		    player.body.y += platform.vy;
	    }
	}
}

function drawGrid(scene) {
	for (let i=0; i<ROWS; i++) {
		scene.add.line(0, 0, 0, TILESIZE*i, WIDTH, TILESIZE*i, 0x1a65ac).setOrigin(0);
	}
	for (let j=0; j<COLS; j++) {
		scene.add.line(0, 0, TILESIZE*j, 0, TILESIZE*j, HEIGHT, 0x1a65ac).setOrigin(0);
	}
}

function randint(a, b) {
	return Math.floor(Math.random() * b + a);
}

function mushroomUp(player,mushroom){
	 
	mushroom.disableBody(true, true);
	 
}

function collectDiamonds(player, diamond) {
		
		diamond.disableBody(true, true);
		diamond_cnt += 1;
		scoreText.setText("score: " + diamond_cnt);

	}