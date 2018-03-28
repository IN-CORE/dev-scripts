package edu.illinois.ncsa.tools.common.exceptions;

public class ParseException extends BaseCommonException
{
	private static final long serialVersionUID = 2013L;

	public ParseException()
	{
		super();
	}

	public ParseException(String message, Throwable cause)
	{
		super(message, cause);
	}

	public ParseException(String message)
	{
		super(message);
	}

	public ParseException(Throwable cause)
	{
		super(cause);
	}
}
