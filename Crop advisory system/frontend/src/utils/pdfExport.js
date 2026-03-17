import jsPDF from 'jspdf';
import 'jspdf-autotable';

export const generateAnalysisReport = (results) => {
  const doc = new jsPDF();
  
  doc.setFontSize(20);
  doc.setTextColor(46, 125, 50);
  doc.text('Crop Analysis Report', 105, 20, { align: 'center' });
  
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 105, 28, { align: 'center' });
  
  let yPos = 40;
  
  doc.setFontSize(16);
  doc.setTextColor(0);
  doc.text('Recommended Crop', 14, yPos);
  yPos += 8;
  
  doc.setFontSize(12);
  doc.setTextColor(46, 125, 50);
  doc.text(results.recommended_crop.toUpperCase(), 14, yPos);
  yPos += 10;
  
  doc.setFontSize(14);
  doc.setTextColor(0);
  doc.text('Soil Health Analysis', 14, yPos);
  yPos += 8;
  
  const soilData = [
    ['Parameter', 'Value', 'Score'],
    ['Nitrogen', `${results.features.N}`, `${Math.round(results.soil_health.component_scores.nitrogen)}%`],
    ['Phosphorus', `${results.features.P}`, `${Math.round(results.soil_health.component_scores.phosphorus)}%`],
    ['Potassium', `${results.features.K}`, `${Math.round(results.soil_health.component_scores.potassium)}%`],
    ['pH Level', `${results.features.ph}`, `${Math.round(results.soil_health.component_scores.ph)}%`]
  ];
  
  doc.autoTable({
    startY: yPos,
    head: [soilData[0]],
    body: soilData.slice(1),
    theme: 'grid',
    headStyles: { fillColor: [76, 175, 80] }
  });
  
  yPos = doc.lastAutoTable.finalY + 10;
  
  if (results.price_analysis) {
    doc.setFontSize(14);
    doc.setTextColor(102, 126, 234);
    doc.text('Market Price Analysis Dashboard', 14, yPos);
    yPos += 8;
    
    // Current Price Box
    doc.setFillColor(255, 140, 66);
    doc.roundedRect(14, yPos, 60, 25, 3, 3, 'F');
    doc.setFontSize(10);
    doc.setTextColor(255, 255, 255);
    doc.text('Current Price', 44, yPos + 8, { align: 'center' });
    doc.setFontSize(16);
    doc.setTextColor(255, 255, 255);
    doc.text(`Rs ${results.price_analysis.current_price}`, 44, yPos + 18, { align: 'center' });
    
    // Trend Box
    const trendColor = results.price_analysis.trend === 'Rising' ? [34, 197, 94] : 
                       results.price_analysis.trend === 'Falling' ? [239, 68, 68] : [245, 158, 11];
    doc.setFillColor(trendColor[0], trendColor[1], trendColor[2]);
    doc.roundedRect(80, yPos, 50, 25, 3, 3, 'F');
    doc.setFontSize(10);
    doc.setTextColor(255, 255, 255);
    doc.text('Trend', 105, yPos + 8, { align: 'center' });
    doc.setFontSize(14);
    doc.text(results.price_analysis.trend, 105, yPos + 18, { align: 'center' });
    
    // Change Box
    const changeColor = results.price_analysis.change_percentage >= 0 ? [34, 197, 94] : [239, 68, 68];
    doc.setFillColor(changeColor[0], changeColor[1], changeColor[2]);
    doc.roundedRect(136, yPos, 60, 25, 3, 3, 'F');
    doc.setFontSize(10);
    doc.setTextColor(255, 255, 255);
    doc.text('Change', 166, yPos + 8, { align: 'center' });
    doc.setFontSize(14);
    const changeText = `${results.price_analysis.change_percentage > 0 ? '+' : ''}${results.price_analysis.change_percentage}%`;
    doc.text(changeText, 166, yPos + 18, { align: 'center' });
    
    yPos += 32;
    
    // Forecast Chart
    if (results.price_analysis.future_prices && results.price_analysis.future_prices.length > 0) {
      doc.setFontSize(12);
      doc.setTextColor(0, 0, 0);
      doc.text('3-Day Price Forecast', 14, yPos);
      yPos += 8;
      
      const chartX = 14;
      const chartY = yPos;
      const chartWidth = 180;
      const chartHeight = 40;
      const barWidth = chartWidth / 3 - 10;
      
      // Draw chart background
      doc.setFillColor(245, 245, 245);
      doc.rect(chartX, chartY, chartWidth, chartHeight, 'F');
      
      const prices = results.price_analysis.future_prices.slice(0, 3);
      const maxPrice = Math.max(...prices, results.price_analysis.current_price);
      const minPrice = Math.min(...prices, results.price_analysis.current_price);
      const priceRange = maxPrice - minPrice || 1;
      
      prices.forEach((price, idx) => {
        const barHeight = ((price - minPrice) / priceRange) * (chartHeight - 15) + 5;
        const barX = chartX + 10 + idx * (barWidth + 15);
        const barY = chartY + chartHeight - barHeight - 5;
        
        const barColor = price > results.price_analysis.current_price ? [34, 197, 94] :
                        price < results.price_analysis.current_price ? [239, 68, 68] : [245, 158, 11];
        doc.setFillColor(barColor[0], barColor[1], barColor[2]);
        doc.roundedRect(barX, barY, barWidth, barHeight, 2, 2, 'F');
        
        doc.setFontSize(8);
        doc.setTextColor(100, 100, 100);
        doc.text(`Day ${idx + 1}`, barX + barWidth / 2, chartY + chartHeight + 3, { align: 'center' });
        doc.setFontSize(9);
        doc.setTextColor(0, 0, 0);
        doc.text(`Rs ${price.toFixed(0)}`, barX + barWidth / 2, barY - 2, { align: 'center' });
      });
      
      yPos += chartHeight + 12;
    }
    
    // Recommendation Box
    doc.setFillColor(76, 175, 80);
    doc.roundedRect(14, yPos, 182, 20, 3, 3, 'F');
    doc.setFontSize(10);
    doc.setTextColor(255, 255, 255);
    doc.text('Expert Recommendation', 105, yPos + 6, { align: 'center' });
    doc.setFontSize(9);
    const recLines = doc.splitTextToSize(results.price_analysis.recommendation, 170);
    doc.text(recLines, 105, yPos + 13, { align: 'center' });
    
    yPos += 28;
  }
  
  doc.setFontSize(14);
  doc.text('Fertilizer Recommendations', 14, yPos);
  yPos += 8;
  
  const fertData = [['Nutrient', 'Fertilizer', 'Quantity']];
  results.fertilizer_recommendations.forEach(rec => {
    fertData.push([rec.nutrient, rec.fertilizer, rec.quantity]);
  });
  
  doc.autoTable({
    startY: yPos,
    head: [fertData[0]],
    body: fertData.slice(1),
    theme: 'grid',
    headStyles: { fillColor: [76, 175, 80] }
  });
  
  doc.save(`Crop_Analysis_${new Date().toISOString().split('T')[0]}.pdf`);
};
