package edu.illinois.ncsa.tools.common;

import org.dom4j.Element;

import java.io.Serializable;

public interface ElementConfigurable extends Serializable
{
	public void initializeFromElement(Element element);
}
