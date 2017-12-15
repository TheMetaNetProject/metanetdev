package edu.berkeley.icsi.metanet.metavisual;

import java.awt.Color;
import java.util.HashMap;

import com.mxgraph.util.mxConstants;

public class GraphStyles {
	
	public GraphStyles() {
	}
	
	public HashMap<String, Object> defaultEdgeStyle() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_CONNECTOR);
		style.put(mxConstants.STYLE_ENDARROW, mxConstants.ARROW_CLASSIC);
		style.put(mxConstants.STYLE_STROKEWIDTH, "1");
		style.put(mxConstants.STYLE_STROKECOLOR, "#000000");
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> reverseEdgeStyle() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_CONNECTOR);
		style.put(mxConstants.STYLE_ENDARROW, mxConstants.ARROW_CLASSIC);
		style.put(mxConstants.STYLE_ROTATION, "180.0");
		style.put(mxConstants.STYLE_STROKEWIDTH, "1");
		style.put(mxConstants.STYLE_STROKECOLOR, Integer.toHexString(Color.BLUE.getRGB()));
		style.put(mxConstants.STYLE_FONTCOLOR, Integer.toHexString(Color.BLUE.getRGB()));
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> schemaMappingEdgeFirst() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_EDGE, mxConstants.EDGESTYLE_TOPTOBOTTOM);
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_CONNECTOR);
		style.put(mxConstants.STYLE_ENDARROW, "none");
		style.put(mxConstants.STYLE_NOLABEL, "true");
		style.put(mxConstants.STYLE_STROKEWIDTH, "2.0");
		style.put(mxConstants.STYLE_STROKECOLOR, Integer.toHexString(Color.RED.getRGB()));
		style.put(mxConstants.STYLE_DASHED, "true");
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> schemaMappingEdgeSecond() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_EDGE, mxConstants.EDGESTYLE_TOPTOBOTTOM);
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_CONNECTOR);
		style.put(mxConstants.STYLE_ENDARROW, mxConstants.ARROW_CLASSIC);
		style.put(mxConstants.STYLE_NOLABEL, "true");
		style.put(mxConstants.STYLE_DASHED, "true");
		style.put(mxConstants.STYLE_STROKEWIDTH, "2.0");
		style.put(mxConstants.STYLE_STROKECOLOR, Integer.toHexString(Color.RED.getRGB()));
		style.put("selectable", "0");
		return style;
	}

	public HashMap<String, Object> schemaBinding() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_CONNECTOR);
		style.put(mxConstants.STYLE_ENDARROW, mxConstants.ARROW_CLASSIC);
		style.put(mxConstants.STYLE_DASHED, "true");
		style.put(mxConstants.STYLE_STROKEWIDTH, "2.0");
		style.put(mxConstants.STYLE_STROKECOLOR, Integer.toHexString(Color.ORANGE.getRGB()));
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> rolesBinding() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_CONNECTOR);
		style.put(mxConstants.STYLE_ENDARROW, mxConstants.NONE);
		style.put(mxConstants.STYLE_STROKEWIDTH, "1.0");
		style.put(mxConstants.STYLE_STROKECOLOR, Integer.toHexString(Color.RED.getRGB()));
		style.put(mxConstants.STYLE_NOLABEL, true);
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> schemaMappingConnector() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_ELLIPSE);
		style.put(mxConstants.STYLE_FILLCOLOR, Integer.toHexString(Color.RED.getRGB()));
		style.put(mxConstants.STYLE_MOVABLE, 0);
		style.put(mxConstants.STYLE_NOLABEL, "true");
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> defaultVertexStyle() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_FONTSIZE, "12");
		style.put(mxConstants.STYLE_FILLCOLOR, "#86b8cf");
		style.put(mxConstants.STYLE_VERTICAL_ALIGN, mxConstants.ALIGN_TOP);
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_RECTANGLE);
		style.put(mxConstants.STYLE_PERIMETER, mxConstants.PERIMETER_RECTANGLE);
		style.put(mxConstants.STYLE_STROKEWIDTH, "0");
		style.put("selectable", "1");
		return style;
	}
	
	public HashMap<String, Object> schemaStyle() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_ALIGN, mxConstants.ALIGN_CENTER);
		style.put(mxConstants.STYLE_FILLCOLOR, "#ededed");
		style.put(mxConstants.STYLE_MOVABLE, 0);
		style.put(mxConstants.STYLE_ROUNDED, true);
		style.put(mxConstants.STYLE_FOLDABLE, 0);
		style.put("selectable", "0");
		return style;
	}
	
	public HashMap<String, Object> schemaMovableStyle() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_ALIGN, mxConstants.ALIGN_CENTER);
		style.put(mxConstants.STYLE_FILLCOLOR, "#ededed");
		style.put(mxConstants.STYLE_ROUNDED, true);
		style.put(mxConstants.STYLE_STROKEWIDTH, "1");
		style.put(mxConstants.STYLE_FOLDABLE, 0);
		style.put("selectable", "1");
		return style;
	}
	
	public HashMap<String, Object> roleStyle() {
		HashMap<String, Object> style = new HashMap<String, Object>();
		style.put(mxConstants.STYLE_FONTSIZE, "10");
		style.put(mxConstants.STYLE_VERTICAL_ALIGN, mxConstants.ALIGN_MIDDLE);
		style.put(mxConstants.STYLE_SHAPE, mxConstants.SHAPE_ELLIPSE);
		style.put(mxConstants.STYLE_PERIMETER, mxConstants.PERIMETER_ELLIPSE);
		style.put(mxConstants.STYLE_MOVABLE, 0);
		style.put(mxConstants.STYLE_WHITE_SPACE, "wrap");
		style.put("selectable", "0");
		return style;
	}
	
}
