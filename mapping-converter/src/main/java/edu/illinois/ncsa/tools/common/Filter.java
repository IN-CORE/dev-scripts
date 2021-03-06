package edu.illinois.ncsa.tools.common;

import edu.illinois.ncsa.tools.common.exceptions.FailedComparisonException;

/**
 * A general filter interface.
 * 
 * @author Albert L. Rossi
 */
public interface Filter
{
	/**
	 * @return true if object satisfies filter; false otherwise.
	 * @throws FailedComparisonException
	 */
	public boolean matches(Object o) throws FailedComparisonException;

}
