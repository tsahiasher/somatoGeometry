function decodeBase64(encoded, dtype) {

    let getter = {
        "float32": "getFloat32",
        "int32": "getInt32"
    }[dtype];

    let arrayType = {
        "float32": Float32Array,
        "int32": Int32Array
    }[dtype];

    let raw = atob(encoded);
    let buffer = new ArrayBuffer(raw.length);
    let asIntArray = new Uint8Array(buffer);
    for (let i = 0; i !== raw.length; i++) {
        asIntArray[i] = raw.charCodeAt(i);
    }

    let view = new DataView(buffer);
    let decoded = new arrayType(
        raw.length / arrayType.BYTES_PER_ELEMENT);
    for (let i = 0, off = 0; i !== decoded.length;
        i++, off += arrayType.BYTES_PER_ELEMENT) {
        decoded[i] = view[getter](off, true);
    }
    return decoded;
}

function getAxisConfig() {
    let axisConfig = {
        showgrid: false,
        showline: false,
        ticks: '',
        title: '',
        showticklabels: false,
            zeroline: false,
        showspikes: false,
        spikesides: false
    };

    return axisConfig;
}

function getLighting() {
    // return {};
    i.e. use plotly defaults:
    {
        "ambient": 0.8,
        "diffuse": .8,
        "fresnel": .2,
        "specular": .05,
        "roughness": .5,
        "facenormalsepsilon": 1e-6,
        "vertexnormalsepsilon": 1e-12
    };
}

function getConfig() {
    let config = {
        modeBarButtonsToRemove: ["hoverClosest3d"],
        displayLogo: false
    };

    return config;
}

function getCamera(plotDivId, viewSelectId) {
    let view = $("#" + viewSelectId).val();
    if (view === "custom") {
        try {
            return $("#" + plotDivId)[0].layout.scene.camera;
        } catch (e) {
            return {};
        }
    }
    let cameras = {
        "left": {eye: {x: -1.7, y: 0, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "right": {eye: {x: 1.7, y: 0, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "flat_left": {eye: {x: -0.006000000000000011, y: 0.0559999999999999, z: 1.68},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: -0.006, y: 0.056, z: -0.003}},
        "s1_left": {eye: {x: -1.01,y: -0.116,z: 1.36},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "insula_left": {eye: {x: -1.6599576485989134, y: 0.12742389556942094, z: -0.34395313008588785},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "sphere_1_left": {eye: {x: -1.4399882133976085, y: 0.5902271075711815, z: 0.684153423410364},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "sphere_2_left": {eye: {x: -0.3336829152795795, y: 0.23698178102481615, z: 1.6499985901547998},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "sphere_3_left": {eye: {x: 1.589452251823426, y: -0.010914944142686027, z: 0.6029281907224133},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "sphere_4_left": {eye: {x: -8.726175157042807e-17, y: 5.675518604139022e-17, z: 1.7},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
		"flat_right": {eye: {x: -0.006000000000000011, y: 0.0559999999999999, z: 1.68},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: -0.006, y: 0.056, z: -0.003}},
        "s1_right": {eye: {x: 0.94,y: 0,z: 1.41},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "insula_right": {eye: {x: 1.6898891128529405, y: 0.0449917296713957, z: -0.21644983373123267},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "sphere_1_right": {eye: {x: 1.5787503116248491, y: 0.39323761287302844, z: 0.4928606632369492},
                    up: {x: 0, y: 0, z: 1},
					center: {x: 0, y: 0, z: 0}},
        "sphere_2_right": {eye: {x: 0.6007777734095456, y: -0.24965813447466756, z: 1.570584885597623},
                    up: {x: -0.8029913907383902, y: -0.44701962052075184, z: 0.39418052370647366},
                    center: {x: 0, y: 0, z: 0}},
        "sphere_3_right": {eye: {x: -1.4835320175510296, y: 0.17664125296290498, z: 0.8111292256186227},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
		"sphere_4_right": {eye: {x: 0.16156040843177574, y: 0.051649448859220376, z: 1.691517238712008},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "top": {eye: {x: 0, y: 0, z: 1.7},
                up: {x: 0, y: 1, z: 0},
                center: {x: 0, y: 0, z: 0}},
        "bottom": {eye: {x: 0, y: 0, z: -1.7},
                    up: {x: 0, y: 1, z: 0},
                    center: {x: 0, y: 0, z: 0}},
        "front": {eye: {x: 0, y: 1.7, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
        "back": {eye: {x: 0, y: -1.7, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}},
    };

    return cameras[view];

}

function getLayout(plotDivId, viewSelectId, blackBg) {

    let camera = getCamera(plotDivId, viewSelectId);
    let axisConfig = getAxisConfig();

    let height = Math.min($(window).outerHeight() * .9,
                            $(window).width() * 2 / 3);
    let width = height * 3 / 2;

    let layout = {
        showlegend: false,
        height: height, width: width,
        margin: {l:0, r:0, b:0, t:0, pad:0},
        hovermode: false,
        paper_bgcolor: blackBg ? '#000': '#fff',
        axis_bgcolor: '#333',
        scene: {
            camera: camera,
            xaxis: axisConfig,
            yaxis: axisConfig,
            zaxis: axisConfig
        }
    };

    return layout;

}

function updateLayout(plotDivId, viewSelectId, blackBg) {
    let layout = getLayout(
        plotDivId, viewSelectId, blackBg);
    Plotly.relayout(plotDivId, layout);
}

function textColor(black_bg){
    if (black_bg){
        return "white";
    }
    return "black";
}

function addColorbar(colorscale, cmin, cmax, divId, layout, config,
                     fontsize=25, height=.5, color="black") {
    // hack to get a colorbar
    let dummy = {
        "opacity": 0,
        "colorbar": {"tickfont": {"size": fontsize, "color": color},
                     "len": height},
        "type": "mesh3d",
        "colorscale": colorscale,
        "x": [1, 0, 0],
        "y": [0, 1, 0],
        "z": [0, 0, 1],
        "i": [0],
        "j": [1],
        "k": [2],
        "intensity": [0.],
        "cmin": cmin,
        "cmax": cmax,
    };

    Plotly.plot(divId, [dummy], layout, config);

}


function decodeHemisphere(surfaceInfo, surface, hemisphere){

    let info = surfaceInfo[surface + "_" + hemisphere];

    for (let attribute of ["x", "y", "z"]) {
        if (!(attribute in info)) {
            info[attribute] = decodeBase64(
                info["_" + attribute], "float32");
        }
    }

    for (let attribute of ["i", "j", "k"]) {
        if (!(attribute in info)) {
            info[attribute] = decodeBase64(
                info["_" + attribute], "int32");
        }
    }

}
