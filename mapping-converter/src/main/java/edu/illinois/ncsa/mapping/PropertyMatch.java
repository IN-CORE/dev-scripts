/*******************************************************************************
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * Contributors:
 *     Shawn Hampton, Jong Lee, Chris Navarro, Nathan Tolbert (NCSA) - initial API and implementation and/or initial documentation
 *******************************************************************************/
package edu.illinois.ncsa.mapping;

import edu.illinois.ncsa.tools.common.UserFacing;
import edu.illinois.ncsa.tools.common.exceptions.ReflectionException;
import edu.illinois.ncsa.tools.common.types.filters.MatchClause;
import edu.illinois.ncsa.tools.common.types.filters.MatchFilter;
import edu.illinois.ncsa.tools.common.types.filters.MatchStatement;
import edu.illinois.ncsa.tools.common.util.FilterUtils;
import org.dom4j.Element;
import org.dom4j.tree.DefaultElement;

import java.util.*;


public class PropertyMatch implements UserFacing {
    private final org.apache.log4j.Logger logger = org.apache.log4j.Logger.getLogger(this.getClass());

    public final static String TAG_SELF = "property-match"; //$NON-NLS-1$
    public final static String TAG_MAP = "map"; //$NON-NLS-1$
    public final static String TAG_ENTRY = "entry"; //$NON-NLS-1$
    public final static String TAG_KEY = "key"; //$NON-NLS-1$
    public final static String TAG_VALUE = "value"; //$NON-NLS-1$
    public final static String TAG_SUCCESS_VALUE = "success-value"; //$NON-NLS-1$
    public final static String TAG_FILTER = "filter"; //$NON-NLS-1$
    public final static String TAG_STATEMENT = "statement"; //$NON-NLS-1$
    public final static String TAG_RULE = "rule"; //$NON-NLS-1$

    private Map<String, String> map = new HashMap<String, String>();
    private String key;
    private MatchFilter matchFilter;

    List<List<String>> rules = new ArrayList<>();
    String ruleString;

    public PropertyMatch(String key, MatchFilter matchFilter) {
        super();
        this.key = key;
        this.matchFilter = matchFilter;
    }

    public PropertyMatch(Element element) {
        initializeFromElement(element);
    }

    public Map<String, String> getMap() {
        return map;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public void setMap(Map<String, String> map) {
        this.map = map;
    }

    public void setMatchFilter(MatchFilter matchFilter) {
        this.matchFilter = matchFilter;
    }

    public MatchFilter getMatchFilter() {
        return matchFilter;
    }

    public List<List<String>> getRules() {
        return rules;
    }

    @SuppressWarnings("unchecked")
    public Element asElement() {
        Element element = new DefaultElement(TAG_SELF);

        Element successValueElement = element.addElement(TAG_SUCCESS_VALUE);

        if (map.isEmpty()) {
            successValueElement.addAttribute(TAG_KEY, key);
        } else {
            Element mapElement = successValueElement.addElement(TAG_MAP);
            for (String key : map.keySet()) {
                String value = map.get(key);
                Element entryElement = mapElement.addElement(TAG_ENTRY);
                entryElement.addAttribute(TAG_KEY, key);
                entryElement.addAttribute(TAG_VALUE, value);
            }
        }

        Element filterElement = element.addElement(TAG_FILTER);
        MatchClause[] clauses = (MatchClause[]) matchFilter.getClauses().toArray(new MatchClause[matchFilter.getClauses().size()]);
        for (MatchClause clause : clauses) {
            Element statementElement = filterElement.addElement(TAG_STATEMENT);
            List statements = clause.getSortedStatements();
            for (Iterator iter = statements.iterator(); iter.hasNext(); ) {
                String statement = (String) iter.next();
                statementElement.addElement(TAG_RULE).setText(statement);
            }
        }

        return element;
    }

    public void initializeFromElement(Element element) {
        map.clear();

        Element successValueElement = element.element(TAG_SUCCESS_VALUE);
        key = successValueElement.attributeValue(TAG_KEY);

        if (key == null) {
            Element mapElement = successValueElement.element(TAG_MAP);
            if (mapElement != null) {
                Iterator<?> iterator = mapElement.elementIterator(TAG_ENTRY);
                while (iterator.hasNext()) {
                    Element entry = (Element) iterator.next();
                    String key = entry.attributeValue(TAG_KEY);
                    String value = entry.attributeValue(TAG_VALUE);
                    map.put(key, value);
                }
            }
        }

        Element filterElement = element.element(TAG_FILTER);
        if (filterElement != null) {
            StringBuilder buffer = new StringBuilder();
            Iterator<?> statementIterator = filterElement.elementIterator(TAG_STATEMENT);
            while (statementIterator.hasNext()) {
                Element statementElement = (Element) statementIterator.next();
                Iterator<?> ruleIterator = statementElement.elementIterator(TAG_RULE);

                List<String> subrules = new ArrayList<>();
                while (ruleIterator.hasNext()) {
                    Element ruleElement = (Element) ruleIterator.next();
                    String rule = ruleElement.getTextTrim();
                    subrules.add(rule);
                    buffer.append(rule);
                    if (ruleIterator.hasNext()) {
                        buffer.append(" && "); //$NON-NLS-1$
                    }
                }
                rules.add(subrules);

                if (statementIterator.hasNext()) {
                    System.out.println("OR used");
                    buffer.append(" || "); //$NON-NLS-1$
                }
            }

            this.ruleString = buffer.toString();

            try {
                matchFilter = FilterUtils.buildFilter(buffer.toString());
            } catch (ReflectionException ex) {
                logger.error("Failed", ex); //$NON-NLS-1$
            } catch (ClassNotFoundException ex) {
                logger.error("Failed", ex); //$NON-NLS-1$
            }
        }
    }

    public String toString() {
        MatchFilter mf = getMatchFilter();
        List<?> clauses = mf.getClauses();

        StringBuilder toString = new StringBuilder(); //$NON-NLS-1$
        for (Object clause : clauses) {
            if (clause instanceof MatchClause) {
                List<?> elements = ((MatchClause) clause).getElements();
                for (Object element : elements) {
                    if (element instanceof MatchStatement) {
                        toString.append(element.toString()).append(","); //$NON-NLS-1$
                    }
                }
            }
        }

        return toString.toString();
    }
}
