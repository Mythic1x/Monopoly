<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" />

    <xsl:template match="ref">
        <a>
            <xsl:attribute name="href">
                #<xsl:value-of select="@kind" />-<xsl:value-of select="@name" />
            </xsl:attribute>
            <xsl:value-of select="@name" />
        </a>
    </xsl:template>

    <xsl:template match="act">
        <a>
            <xsl:attribute name="href">
                #action-<xsl:value-of select="@name" />
            </xsl:attribute>
            <xsl:value-of select="@name" />
        </a>
    </xsl:template>

    <xsl:template match="action">
        <div class="action">
            <h3>
                <xsl:attribute name="id">action-<xsl:value-of select="name" /></xsl:attribute>
                <xsl:value-of select="name" />
            </h3>

            <xsl:if test="arg">
                <dl>
                    <center><i>args</i></center>
                    <xsl:for-each select="arg">
                        <dt><xsl:value-of select="name" /> (<xsl:apply-templates select="type" />)</dt>
                        <dd><xsl:apply-templates select="desc" /></dd>
                    </xsl:for-each>
                </dl>
            </xsl:if>

            <xsl:if test="desc">
                <p><xsl:apply-templates select="desc" /></p>
            </xsl:if>
            <xsl:if test="reply">
                Responses:
                <ul>
                    <xsl:for-each select="reply/ref">
                        <li><xsl:apply-templates select='.' /></li>
                    </xsl:for-each>
                </ul>
            </xsl:if>
        </div>

    </xsl:template>

    <xsl:template match="resp">
        <div class="resp">
            <h3>
                <xsl:attribute name="id">response-<xsl:value-of select="name" /></xsl:attribute>
                <xsl:value-of select="name" />
            </h3>
            <p>value: 
                <xsl:apply-templates select="value" />
            </p>
            <xsl:if test="desc">
                <p>
                    <xsl:apply-templates select="desc" />
                </p>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="ty">
        <div class="ty">
            <h3>
                <xsl:attribute name="id">type-<xsl:value-of select="name" /></xsl:attribute>
                <xsl:value-of select="name" />
            </h3>
            <xsl:if test="desc">
                <p><xsl:apply-templates select="desc" /></p>
            </xsl:if>
            <xsl:if test="prop">
                <dl>
                    <xsl:for-each select="prop">
                        <dt><xsl:value-of select="@name" /></dt>
                        <dd>
                            <xsl:choose>
                                <xsl:when test="@type">
                                    <xsl:value-of select="@type" />
                                </xsl:when>

                                <xsl:otherwise>
                                    <xsl:apply-templates select="./type" />
                                </xsl:otherwise>
                            </xsl:choose>
                        </dd>
                    </xsl:for-each>
                </dl>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="/">
        <style>
            body {
                margin: 1em;
                font-family: arial, sans-serif;
            }

            dl {
                margin-left: 1em;
                padding: 1em;
                background: white;
                width: fit-content;
                border-radius: 2px;
            }
            dt {
                font-weight: bold;
            }

            .action, .ty, .resp {
                background: lightblue;
                padding: 1em;
                margin: 1em;
                border-radius: 2px;

                max-width: 500px;
                text-wrap: wrap;
            }
            </style>
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                <title>Docs</title>
            </head>
            <body>
                <h1>Docs</h1>
                <h2>Actions</h2>
                <xsl:apply-templates select="/data/actions/action" />
                <hr />
                <h2>Responses</h2>
                <xsl:apply-templates select="/data/responses/resp" />
                <hr />
                <h2>Types</h2>
                <xsl:apply-templates select="/data/types/ty" />
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
