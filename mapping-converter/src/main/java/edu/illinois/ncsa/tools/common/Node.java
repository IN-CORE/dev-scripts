package edu.illinois.ncsa.tools.common;

public interface Node
{
	public static final String TAG_SELF = "node";

	public Node[] getChildren();

	public void setChildren(Node[] children);

	public Node[] getDependencies();

	public void setDependencies(Node[] dependencies);

	public String getName();

	public void setName(String name);

	public void setChildNames(String[] names);

	public void setDependencyNames(String[] names);

	public String[] getChildNames();

	public String[] getDependencyNames();

	public void addChild(Node child) throws IllegalArgumentException;

	public void addDependency(Node dependency) throws IllegalArgumentException;

	public void addChildName(String name);

	public void addDependencyName(String name);

	public void removeChild(Node child);

	public void removeDependency(Node dependency);

	public void removeChildName(String name);

	public void removeDependencyName(String name);
}
