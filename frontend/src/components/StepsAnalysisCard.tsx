import React, { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Highlight, themes } from "prism-react-renderer"
import { Copy, Check } from 'lucide-react'
import { useToast } from "@/hooks/use-toast"

interface Props {
    content: string
}

export default function StepsAnalysisCard({ content }: Props) {
    const [copied, setCopied] = useState(false)
    const [text, setText] = useState('')
    const { toast } = useToast()

    useEffect(() => {
        let i = 0;

        setTimeout(() => {
            const interval = setInterval(() => {
                setText(content.slice(0, i))
                i++;
                if (i > content.length) clearInterval(interval)
            }, 20)
        }, 60)

    }, [content])

    const copyToClipboard = () => {
        navigator.clipboard.writeText(content).then(() => {
            setCopied(true)
            toast({
                title: "Copied to clipboard",
                description: "The JSON has been copied to your clipboard.",
            })
            setTimeout(() => setCopied(false), 2000)
        })
    }

    return (
        <div className="w-full lg:w-1/2 h-full">
            <Card className="w-full h-full">
                <CardHeader>
                    <CardTitle className="text-xl font-semibold flex justify-between items-center">
                        Steps Analysis
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={copyToClipboard}
                            aria-label="Copy to clipboard"
                        >
                            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </Button>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <Highlight theme={themes.github} code={text} language="tsx">
                        {({ className, style, tokens, getLineProps, getTokenProps }) => (
                            <pre className={className + ' transition-all duration-700'}
                                style={{ ...style, padding: "0px 10px", height: "100%", textWrap: "wrap", maxHeight: "500px", overflowY: "auto", borderRadius: "5px" }}>
                                {tokens.map((line, i) => (
                                    <div key={i} {...getLineProps({ line })}>
                                        {line.map((token, key) => (
                                            <span key={key} {...getTokenProps({ token })} />
                                        ))}
                                    </div>
                                ))}
                            </pre>
                        )}
                    </Highlight>
                </CardContent>
            </Card>

        </div>
    )
}
