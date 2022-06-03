// 움직이는 플랫폼 생성 
//움직이는 발판들 
class MovingPlatform extends Phaser.GameObjects.Sprite {
	constructor(config) {
		super(config.scene, config.x, config.y, 'movingp')
		config.scene.add.existing(this);
		config.scene.physics.add.existing(this);

		this.config = config;
		this.setScale(0.4);
		//중력 x 
		this.allowGravity = false;
		// 왼쪽오른쪽 움직이는거 
		if (config.type == 'side') {
			config.scene.tweens.add({
				targets : this.body.velocity,
				// x -150 ~ 150 이동하기 
				x : {from: -150, to: 150},
				ease: Phaser.Math.Easing.Quadratic.InOut,
				yoyo: true,
				repeat: -1,
				duration: 1000,
				delay: Phaser.Math.Between(0,6) * 200,
				onUpdate: () => {
	                this.vx = this.body.position.x - this.previousX;
	                this.vy = this.body.position.y - this.previousY;
	                this.previousX = this.body.position.x;
	                this.previousY = this.body.position.y;
	            }
			})
		}
		// 위아래로 움직이는거 
		if (config.type == 'up') {
			config.scene.tweens.add({
				targets : this.body.velocity,
				// y 의 -150 위치부터 150 까지 움직이기 
				y : {from: -150, to: 150},
				ease: Phaser.Math.Easing.Quadratic.InOut,
				yoyo: true,
				repeat: -1,
				duration: 1000,
				delay: Phaser.Math.Between(0,6) * 200,
				onUpdate: () => {
	                this.vx = this.body.position.x - this.previousX;
	                this.vy = this.body.position.y - this.previousY;
	                this.previousX = this.body.position.x; 
	                this.previousY = this.body.position.y;
	            },
			})
		}
		
	}
}