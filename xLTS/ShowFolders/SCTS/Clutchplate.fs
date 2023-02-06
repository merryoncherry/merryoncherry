/*{
	"DESCRIPTION": "Bounces a gradient between upper and lower boundary, optionally as a dual",
	"CREDIT": "by Clutchplate",
	"ISFVSN": "2.0",
	"CATEGORIES": [
		"TEST-GLSL"
	],
	"INPUTS": [
		{
			"LABEL": "Color",
			"NAME": "color",
			"TYPE": "color",
			"DEFAULT": [0.5,0.5,0.5]
		},
		{
			"LABEL": "Thickness",
			"NAME": "thickness",
			"TYPE": "float",
			"DEFAULT": 0.2,
			"MIN": 0.01,
			"MAX": 5.0
		},
		{
			"LABEL": "Rotation",
			"NAME": "angle",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 360.0
		},
		{
			"LABEL": "Dual",
			"NAME": "dual",
			"TYPE": "bool",
			"DEFAULT": false
		},
		{
			"LABEL": "Cycle Count",
			"NAME": "cycles",
			"TYPE": "float",
			"DEFAULT": 1.0,
			"MIN": -16.0,
			"MAX": 16.0
		}
	]
}*/

float frac(float f)
{
    // The epsilon is to prevent the final frame to revert to the beginning value
    return f<0.0 ? 1.0-(-f-floor(-f+0.000001)) : (f-floor(f-0.000001));
}

// loc is -0.5 to 0.5
float mixcolor(float loc){
    float normTimeInEffect = frac(TIME * cycles / XL_DURATION) - 0.5;
    // normTimeInEffect maps to -0.5 to 0.5 now

    float midc = (1.0 - 2.0 * abs((loc - normTimeInEffect) * (1.0 / thickness)));
    return midc;
}

void main()	{
    float p2x = isf_FragNormCoord.x-0.5;
    float p2y = isf_FragNormCoord.y-0.5;
    float rads = angle*3.1415927/180.0;
    float px = p2x*sin(rads)+p2y*cos(rads);
    float py = p2x*cos(rads)-p2y*sin(rads);
    // px,py are in -0.5 to 0.5 range
    
    float mult = mixcolor(py);
    float mult2 = mixcolor(-py);
    vec4 col1  = vec4(mult * color[0],mult * color[1],mult * color[2],1.0);
    vec4 col2 = vec4(mult2 * color[0],mult2 * color[1],mult2 * color[2],1.0);
    gl_FragColor=dual ? 
      vec4(
        max(col1[0],col2[0]),
        max(col1[1],col2[1]),
        max(col1[2],col2[2]),
        1.0
      )
      :
      col1;
}


