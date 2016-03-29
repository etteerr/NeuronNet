/**
 * Created by shanshi on 16-3-2016.
 */
site = document.getElementById('content');

stage = new createjs.Stage("mainCanvas");

//Create cirlce
circle = new createjs.Shape();
circle.graphics.beginFill("red").drawCircle(0,0,40);
circle.x = circle.y = 50;
stage.addChild(circle);
stage.update();

