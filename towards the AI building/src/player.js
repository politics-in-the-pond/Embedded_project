class Player extends Phaser.GameObjects.Sprite {
	constructor(config) {
		super(config.scene, config.x, config.y, 'student');
		config.scene.add.existing(this);
		config.scene.physics.add.existing(this);

		this.body.setGravityY(300);
		this.body.setBounce(0.2);
		this.body.setCollideWorldBounds(true);
		// 움직임 설정 
		config.scene.anims.create({
	        key: 'left',
			//왼쪽 방향의 asset 사진 배열 0~3 
	        frames: config.scene.anims.generateFrameNumbers('student', {start: 9, end: 14}),
	        frameRate: 10,
	        repeat: -1
	    })

		config.scene.anims.create({
	        key: 'turn',
			//오른쪽 방향의 asset 사진 배열 5~8 
	        frames: config.scene.anims.generateFrameNumbers('student', {start: 0, end: 8}),
	        frameRate: 7,
	        repeat: -1
	    })

	    config.scene.anims.create({
	        key: 'right',
			//오른쪽 방향의 asset 사진 배열 5~8 
	        frames: config.scene.anims.generateFrameNumbers('student', {start: 15, end: 20}),
	        frameRate: 10,
	        repeat: -1
	    })
	}
}