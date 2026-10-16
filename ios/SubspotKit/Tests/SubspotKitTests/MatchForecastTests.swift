import XCTest
@testable import SubspotKit

final class MatchForecastTests: XCTestCase {
    func testValidForecastPicksMostLikelyOutcome() throws {
        let forecast = try MatchForecast(
            homeTeam: "arsenal", awayTeam: "wolves", homeWin: 0.72, draw: 0.18, awayWin: 0.10
        )
        XCTAssertEqual(forecast.mostLikely, .homeWin)
        XCTAssertEqual(forecast.probability(of: .draw), 0.18, accuracy: 1e-12)
    }

    func testRejectsProbabilitiesThatDoNotSumToOne() {
        XCTAssertThrowsError(
            try MatchForecast(homeTeam: "a", awayTeam: "b", homeWin: 0.5, draw: 0.5, awayWin: 0.5)
        ) { error in
            guard let validationError = error as? MatchForecast.ValidationError,
                  case .probabilitiesDoNotSumToOne = validationError else {
                return XCTFail("Unexpected error: \(error)")
            }
        }
    }

    func testRejectsNegativeProbability() {
        XCTAssertThrowsError(
            try MatchForecast(homeTeam: "a", awayTeam: "b", homeWin: 1.1, draw: -0.1, awayWin: 0.0)
        )
    }

    func testDecodesSnakeCaseApiPayloadAndValidates() throws {
        let json = Data("""
        {"home_team": "liverpool", "away_team": "chelsea", "home_win": 0.55, "draw": 0.25, "away_win": 0.20}
        """.utf8)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        let forecast = try decoder.decode(MatchForecast.self, from: json)
        XCTAssertEqual(forecast.homeTeam, "liverpool")
        XCTAssertEqual(forecast.mostLikely, .homeWin)
    }

    func testDecodingInvalidPayloadThrows() {
        let json = Data("""
        {"home_team": "a", "away_team": "b", "home_win": 0.9, "draw": 0.9, "away_win": 0.9}
        """.utf8)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        XCTAssertThrowsError(try decoder.decode(MatchForecast.self, from: json))
    }
}
